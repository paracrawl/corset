import os
import re
import shutil
import subprocess
import time
import xml
from datetime import datetime

from back.bo.file_formats_bo import FileFormatsBO
from back.bo.lang_formats_bo import LangFormatsBO
from back.bo.query_corpus_bo import QueryCorpusBO
from back.bo.query_request_bo import QueryRequestBO
from back.bo.status_bo import StatusBO
from back.bo.user_bo import UserBO
from back.dto.custom_corpus import CustomCorpus

from back.dto.query_corpus import QueryCorpus
from werkzeug.utils import escape, secure_filename

from back.dto.query_request import QueryRequest

from celery import Celery

from back.config import Config
from back.api.config import Config as APIConfig
from back.bo.langs_bo import LangsBO
from back.bo.base_corpus_bo import BaseCorpusBO
from back.bo.custom_corpus_bo import CustomCorpusBO, identify_langs

celery = Celery('dp-back', broker=Config.CELERY_BROKER_URL)
celery.config_from_object(Config())

from celery.utils.log import get_task_logger
celery_logger = get_task_logger(__name__)


@celery.task(bind=True)
def generate_corset(self, user_id, tmp_path, filename, collection_id,
                    src_lang_id, trg_lang_id, out_format, size_label, name, topic_id):
    file_path, parallel_fallback = process_upload(tmp_path, filename)

    # Get User DTO
    user_bo = UserBO()
    user_dto = user_bo.get_user(user_id)

    # Get language codes
    langs_bo = LangsBO()
    source_lang = langs_bo.get_lang(src_lang_id)
    target_lang = langs_bo.get_lang(trg_lang_id)

    # Identify languages
    src_sentences = []
    trg_sentences = []
    with open(file_path, 'r') as sentences_file:
        for i, row in enumerate(sentences_file):
            if i < 10:
                sentences = row.strip().split('\t')
                src_sentences.append(sentences[0])
                if len(sentences) > 1:
                    trg_sentences.append(sentences[1])

    try:
        [lang, side, lang2, side2, parallel, _] = identify_langs(src_sentences, trg_sentences,
                                                                 source_lang.code, target_lang.code)
    except:
        parallel = parallel_fallback

        if parallel:
            lang = source_lang.code
            side = 'src'
            lang2 = target_lang.code
            side2 = 'trg'
        else:
            lang = target_lang.code
            side = 'trg'
            lang2 = source_lang.code
            side2 = 'src'

    # We need to know how many sentences we want
    sentences = Config.CORSET_SIZE[size_label] if size_label in Config.CORSET_SIZE else Config.CORSET_SIZE['small']

    # Get file format
    file_formats_bo = FileFormatsBO()
    file_formats = file_formats_bo.get_fileformats()
    file_format = [f for f in file_formats if f.file_format == out_format][0]

    # Get lang format
    lang_formats_bo = LangFormatsBO()
    lang_formats = lang_formats_bo.get_langformats()
    lang_format = [f for f in lang_formats if f.lang_format == ('parallel' if parallel else 'mono')][0]

    # Build Query Corpus
    query_corpus_bo = QueryCorpusBO()
    query_corpus: QueryCorpus = QueryCorpus(file_format=file_format, lang_format=lang_format, source_lang=source_lang,
                                            target_lang=target_lang, sentences=sentences, location=file_path,
                                            is_active=True, size=0)
    query_corpus = query_corpus_bo.add_query_corpus(query_corpus)

    # Get collection name
    base_corpus_bo = BaseCorpusBO()
    base_corpus = base_corpus_bo.get_base_corpus(collection_id)
    collection = base_corpus_bo.get_collection(collection_id)

    # Generate corset paths
    corset_dir = "corset-{}-{}-{}-{}".format(user_id, source_lang.code, target_lang.code, time.time())
    corset_dir_path = os.path.join(Config.CORSETS_FOLDER, corset_dir)
    os.mkdir(corset_dir_path)

    corset_base_name = "{}-{}-{}".format(name, collection, time.time())
    corset_base_name = secure_filename(corset_base_name)
    output_file = os.path.join(corset_dir_path, "{}.corset.{}".format(corset_base_name,
                                                                      'tmx' if out_format == 'tmx' else 'tsv'))
    config_file = os.path.join(corset_dir_path, "{}.config".format(corset_base_name))

    # Build config file
    custom_corpus_bo = CustomCorpusBO()
    custom_corpus_bo.build_config_file(config_file, file_path, output_file, sentences, collection, lang,
                                       side, lang2, side2, parallel, out_format)

    # Get task status
    status = get_task_status(self.request.id)

    # Build Query Request
    query_request_bo = QueryRequestBO()
    query_request: QueryRequest = QueryRequest(owner=user_dto.user_id, name=escape(name), creation_date=datetime.now(),
                                               base_corpus=base_corpus.corpus_id, query_corpus=query_corpus.corpus_id,
                                               job_id=str(self.request.id), status=status.status_id)
    query_request = query_request_bo.add_query_request(query_request)

    monitor_request_status.apply_async(args=[self.request.id, query_request.request_id])

    # Pray
    work_the_miracle(config_file)

    # The Miracle blesses the user with lots of information about the generated sentences,
    # but we don't really want the user to know where they came from... so we're basically
    # defying God here
    filtered_miracle_output = defy_god(output_file, out_format)

    # We keep the original corset for generating samples
    sample_output_file = "{}-sampler".format(output_file)
    shutil.move(output_file, sample_output_file)

    # And then we save the filtered corset as the main corset
    shutil.move(filtered_miracle_output, output_file)

    # We compress the corset so users can download it faster
    zip_output_file = "{}.zip".format(output_file)
    subprocess.check_output("zip -j {} {}".format(zip_output_file, output_file), shell=True)

    # We store a sample of the corset in a solr collection, we generate
    # a prefix to identify the samples belonging to this corset
    sample_solr_prefix = "{}-{}-{}".format(source_lang.code.upper(), target_lang.code.upper(), query_request.request_id)

    # Get size of generated ZIP file
    size = os.stat(zip_output_file).st_size

    # Save corset in database
    custom_corpus_bo = CustomCorpusBO()
    custom_corpus: CustomCorpus = CustomCorpus(corpus_id=None, name=name,
                                               source_lang=source_lang.lang_id,
                                               target_lang=target_lang.lang_id,
                                               sentences=sentences, size=size,
                                               solr_collection="custom-samples", is_active=True, is_highlight=False,
                                               description='',
                                               file_format=file_format.format_id,
                                               location=zip_output_file,
                                               solr_prefix=sample_solr_prefix, topics=[topic_id], last_download=None,
                                               num_downloads=0, is_private=True,
                                               creation_date=datetime.now())

    custom_corpus = custom_corpus_bo.add_custom_corpus(custom_corpus)
    query_request_bo.update_query_request_custom_corpus(query_request.request_id, custom_corpus.corpus_id)

    # We extract sentences for the sample
    sample_path = extract_sample(sample_output_file, out_format)

    # We upload the sample to solr
    txt2solr_path = os.path.join(Config.SCRIPTS_FOLDER, "txt2solr.py")
    subprocess.check_output("head -n {sample_size} {sample_path} | tee {output_file}-sample-extract && "
                            "python3.7 {script_path} -c \"{solr_url}/custom-samples\" "
                            "-p {solr_prefix} --liteformat {output_file}-sample-extract "
                            "-u {solr_user} -w {solr_pwd}".format(sample_size=Config.CORPORA_SAMPLE_SIZE,
                                                                  sample_path=sample_path,
                                                                  output_file=output_file, script_path=txt2solr_path,
                                                                  solr_prefix=sample_solr_prefix,
                                                                  solr_url=os.environ['SOLR_URL'],
                                                                  solr_user=os.environ['SOLR_USR'],
                                                                  solr_pwd=os.environ['SOLR_PWD']),
                            shell=True)

    # Clean up
    try:
        # We remove the generated config file for miracle.py
        # If this fails, we don't really care
        os.remove(config_file)

        # We remove files uploaded by user
        if query_corpus.location:
            os.remove(query_corpus.location)
    except:
        pass

    return zip_output_file
    

def work_the_miracle(config_file):
    miracle_path = os.path.join(Config.SCRIPTS_FOLDER, "miracle.py")

    miracle_output = subprocess.check_output("python3 {} {}".format(miracle_path, config_file), shell=True)
    return miracle_output


def defy_god(miracle_output, out_format):
    filtered_miracle_output = "{}-filtered".format(miracle_output)
    if out_format == 'tsv':
        subprocess.check_output(
            "cat {} | cut -f3,4 > {}".format(miracle_output, filtered_miracle_output), shell=True)
    elif out_format == 'tmx':
        subprocess.check_output(
            "cat {} | sed '/^\\s*<prop/d' > {}".format(miracle_output, filtered_miracle_output), shell=True)

    return filtered_miracle_output


def process_upload(tmp_path, filename):
    path = os.path.join(APIConfig.UPLOAD_FOLDER, filename)
    shutil.move(tmp_path, path)

    # Remove BOM (if present)
    no_bom = subprocess.Popen("sed -i '1s/^\\xEF\\xBB\\xBF//' {path}".format(path=path), shell=True)
    no_bom.wait()

    # Convert whatever format this has to UTF-8
    convert_process = subprocess.Popen(
        "cat {path} | iconv -f $(cat {path} | head -n 1000 "
        "| chardetect | awk '{{print $2}}') -t utf-8 > {path}.utf8".format(path=path),
        shell=True
    )
    convert_process.wait()

    replace_process = subprocess.Popen("mv {path}.utf8 {path}".format(path=path), shell=True)
    replace_process.wait()

    # Detect input format
    xml_declaration = False
    tmx_declaration = False
    with open(path, 'r') as input_file:
        for i, line in enumerate(input_file):
            try:
                line.index('<?xml')
                xml_declaration = True
            except ValueError:
                pass

            try:
                line.index('<tmx')
                tmx_declaration = True
            except ValueError:
                pass

            if i > 0:
                break

    input_format = 'tmx' if (xml_declaration and tmx_declaration) else 'tsv'

    # Let's parse!
    output_path = "{}-output".format(path)
    bilingual = False
    if input_format == 'tsv':
        # Take the first [line_limit] lines
        line_limit = Config.CORPORA_LINE_LIMIT
        limit_path = "{}.limit".format(path)
        limit_process = subprocess.Popen(
            "cat {path} | head -n {limit} > {limit_path}".format(path=path, limit=line_limit, limit_path=limit_path),
            shell=True
        )
        limit_process.wait()

        shutil.move(limit_path, output_path)

        with open(output_path, 'r') as output_file:
            first_line = output_file.readline()
            parts = first_line.split('\t')
            bilingual = len(parts) > 1 and parts[1] != ''
    elif input_format == 'tmx':
        with open(path, 'rb') as inputFile, open(output_path, 'w') as output:
            inside_tuv = False
            seg_text = []
            tu = []
            count = 0

            def se(name, _):
                nonlocal inside_tuv
                if name == "seg":
                    inside_tuv = True

            def lp(line):
                return re.sub(r'[\r\n\t\f\v]', " ", line.strip())

            def ee(name):
                nonlocal inside_tuv, seg_text, tu, bilingual, count
                if name == "seg":
                    inside_tuv = False
                    tu.append("".join(seg_text).strip())
                    seg_text = []

                if name == "tu":
                    if count < Config.CORPORA_LINE_LIMIT:
                        if len(tu) > 0:
                            bilingual = len(tu) > 1
                            count = count + 1

                            print('\t'.join(tu), file=output)
                            tu = []

            def cd(data):
                nonlocal inside_tuv, seg_text
                if inside_tuv:
                    seg_text.append(data)

            parser = xml.parsers.expat.ParserCreate()
            parser.StartElementHandler = se
            parser.EndElementHandler = ee
            parser.CharacterDataHandler = cd
            parser.ParseFile(inputFile)

    return output_path, bilingual


def extract_sample(output_path, out_format):
    sample_path = "{}-sample".format(output_path)

    if out_format == 'tsv':
        shutil.copy(output_path, sample_path)
        return output_path
    else:
        with open(output_path, 'rb') as output_file, open(sample_path, 'w') as sample_file:
            inside_tuv = False
            seg_text = []
            tuv = []
            tu = []

            inside_prop = False
            props = {}
            prop_type = None

            def se(name, attrs):
                nonlocal inside_tuv, inside_prop, props, prop_type
                if name == "seg":
                    inside_tuv = True
                elif name == "prop":
                    inside_prop = True
                    prop_type = attrs['type']
                    if prop_type not in props:
                        props[prop_type] = []

            def ee(name):
                nonlocal inside_tuv, seg_text, tuv, inside_prop, props, tu, prop_type
                if name == "seg":
                    inside_tuv = False
                    tuv.append(''.join(seg_text).strip())
                    seg_text = []
                elif name == "prop":
                    inside_prop = False
                elif name == "tuv":
                    if len(tuv) > 0:
                        tu.append([
                            ''.join(props['source-document']).strip(),
                            tuv[0]
                        ])

                        tuv = []
                elif name == "tu":
                    if len(tu) > 0:
                        sources = [c[0] for c in tu]
                        texts = [c[1] for c in tu]
                        score = ''.join(props['custom-score']).strip()

                        row = sources + texts + [score]
                        print('\t'.join(row), file=sample_file)

                        tu = []
                        props = {}

            def cd(data):
                nonlocal inside_tuv, seg_text, props, prop_type
                if inside_tuv:
                    seg_text.append(data)
                if inside_prop:
                    props[prop_type].append(data)

            parser = xml.parsers.expat.ParserCreate()
            parser.StartElementHandler = se
            parser.EndElementHandler = ee
            parser.CharacterDataHandler = cd
            parser.ParseFile(output_file)

    return sample_path


@celery.task()
def monitor_request_status(task_id, query_request_id):
    def monitor():
        status = get_task_status(task_id)
        query_request_bo = QueryRequestBO()
        query_request_bo.update_query_request_status(query_request_id, status.status_id)

        if status.status in ['STARTED', 'PENDING', 'RETRY']:
            time.sleep(1)
            monitor()

        if status.status == 'SUCCESS':
            pass

    monitor()


def get_task_status(task_id):
    task_info = generate_corset.AsyncResult(task_id)
    celery_status = task_info.status

    status_bo = StatusBO()
    statuses = status_bo.get_statuses()
    status = [s for s in statuses if s.status == celery_status]
    return status[0]
