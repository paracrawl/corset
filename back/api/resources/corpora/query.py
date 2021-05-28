import tempfile
import time

from flask_login import login_required, current_user
from flask_restx import Resource, reqparse
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

from back.tasks import tasks


class Query(Resource):

    @login_required
    def post(self):

        parser = reqparse.RequestParser()
        parser.add_argument('name', type=str, required=True, help='Corset name')
        parser.add_argument('topic', type=int, required=True, help='ID of topic')
        parser.add_argument('size', type=str, required=True, help='Size: small, medium, large')
        parser.add_argument('download_format', type=str, required=True, help='Download format: tsv, tmx')
        parser.add_argument('file', type=FileStorage, location='files', required=True, help='Corpus file')
        parser.add_argument('source_lang', type=int, required=True, help='Code of source language')
        parser.add_argument('target_lang', type=int, required=True, help='Code of target language')
        parser.add_argument('collection', type=int, required=True, help='SOLR corpus collection')
        args = parser.parse_args(strict=True)

        file = args['file']
        filename = "{}-{}-{}".format(current_user.id, file.filename, time.time())
        filename = secure_filename(filename)

        tmp_file = tempfile.NamedTemporaryFile(delete=False)
        file.save(tmp_file)
        file.close()

        download_format = 'tmx' if args['download_format'] == 'tmx' else 'tsv'

        task = tasks.generate_corset.apply_async(args=[current_user.id, tmp_file.name, filename, args['collection'],
                                                       args['source_lang'], args['target_lang'], download_format,
                                                       args['size'], args['name'], args['topic']])
        task_id = task.id

        return {'task_id': task_id}, 201
