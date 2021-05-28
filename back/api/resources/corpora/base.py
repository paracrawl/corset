from back.dto.sentence import Sentence
from flask_login import login_required
from flask_restx import Resource, reqparse

from back.bo.base_corpus_bo import BaseCorpusBO
from back.dto.base_corpus import BaseCorpus

class Base(Resource):

    @login_required
    def get(self, corpus_id=None, source_lang=None, target_lang=None):
        base_corpus_bo = BaseCorpusBO()

        parser = reqparse.RequestParser()
        parser.add_argument('preview', type=bool, help='Return preview')
        parser.add_argument('preview_rows', type=int, help='Number of preview sentences')
        parser.add_argument('preview_start', type=int, help='Offset of preview sentences')
        args = parser.parse_args(strict=True)

        if corpus_id:
            response = {}

            base_corpus = base_corpus_bo.get_base_corpus(corpus_id)
            response['base_corpus'] = BaseCorpus.schema().dump(base_corpus)

            if args['preview']:
                start = args['preview_start']
                rows = args['preview_rows'] if args['preview_rows'] else 10
                rows = rows if rows < 100 else 100

                preview_sentences = base_corpus_bo.get_base_corpus_preview(corpus_id, rows=rows, start=start)
                response['preview_sentences'] = Sentence.schema().dump(preview_sentences, many=True)

            if response and response['base_corpus']:
                return response, 200
            else:
                return None, 404
        elif source_lang and target_lang:
            base_corpora = base_corpus_bo.get_base_corpora_by_pair(source_lang, target_lang)
            if base_corpora:
                return BaseCorpus.schema().dump(base_corpora, many=True), 200
            return [], 404
        else:
            base_corpora = base_corpus_bo.get_available_base_corpora()
            if base_corpora:
                return BaseCorpus.schema().dump(base_corpora, many=True), 200
            return [], 404
