import os
import logging
from glob import glob
from mutagen.flac import FLAC
from somnilopy import settings
from somnilopy.exceptions import LabelNotAllowedError


class FolderHandler:
    def __init__(self, folder='recordings', file_name_prefix='autosave'):
        self.file_prefix = file_name_prefix
        self.folder = folder
        self.label = None
        for label in settings.LABELS:
            dir = os.path.join(settings.PREFIX_DIR, label)
            if not os.path.exists(dir):
                os.makedirs(dir)

    def get_file_path_from_name(self, name):
        try:
            rel_path = glob(os.path.join(self.folder, '*', name))[0]
        except IndexError:
            logging.debug(f'Tried to get file path for file {name} but couldn''t find file')
            raise FileNotFoundError
        return rel_path

    def get_label_from_name(self, name):
        rel_path = self.get_file_path_from_name(name)
        label = os.path.split(rel_path)[1]
        return label

    @classmethod
    def update_comment(cls, audio, comment):
        """
        Takes path to an FLACC file and comment string and adds Vorbis comment string
        """
        audio["Comment"] = comment
        audio.save()
        return True

    def update_comment_from_name(self, name, comment):
        """
        Takes path to an FLACC file and comment string and adds Vorbis comment string
        """
        path = self.get_file_path_from_name(name)
        self.update_comment_from_path(path, comment)
        return True

    def update_comment_from_path(self, path, comment):
        """
        Takes path to an FLACC file and comment string and adds Vorbis comment string
        """
        logging.info(f'Adding comment "{comment}" to file at path {path}')
        audio = FLAC(path)
        self.update_comment(audio, comment)
        return True

    def get_comment(self, name):
        """
        Reads comment of FLAC file
        """
        path = self.get_file_path_from_name(name)
        audio = FLAC(path)
        try:
            return audio["Comment"][0]
        except KeyError:
            return '(null)' # Don't return an actual None, but return something nicely formatted

    def apply_label(self, name, new_label):
        """
        Move a file from one folder to another. This acts as a pseudo persistent label without having to
        modify comments or metadata. Having all the 'sleeptalking' and 'not sleeptalking' files in their
        respective folders also makes it easier to train models
        :param old_label:
        :param new_label:
        :param name:
        :return:
        """
        # Make sure we have that file, else send a 404
        if new_label not in settings.LABELS and new_label.lower() != 'delete':
            raise LabelNotAllowedError
        # Move to label named folder
        current_path = self.get_file_path_from_name(name)
        new_path = os.path.join(self.folder, new_label, name)
        os.rename(current_path, new_path)
        logging.debug(f'Moved file from {current_path} to {new_path}')
        return 200

    @staticmethod
    def get_all_file_paths():
        """
        :return:
        """
        all_file_paths = []
        for label in settings.LABELS:
            dir = os.path.join(settings.PREFIX_DIR, label)
            all_file_paths.extend([os.path.join(dir, file_name) for file_name in os.listdir(dir)])
        logging.debug(f'Got {len(all_file_paths)} file paths')
        all_file_paths.sort(key=lambda x: os.path.getmtime(x))
        return all_file_paths

    def get_file_info_by_name(self, name):
        path = self.get_file_path_from_name(name)
        return self.get_file_info_by_path(path)

    def get_file_info_by_path(self, path):
        if not os.path.isfile(path):
            raise FileNotFoundError
        try:
            date, time = path.split("_")[1:3]
            time = time.replace(".flac", "")
            time = time.replace("-", ":")[0:8]
            label, name = os.path.split(path)
            label = os.path.split(label)[1]
            comment = self.get_comment(name)
            if path.endswith(".flac"):
                f = FLAC(path)
                length = f.info.length
                return [{"date": date,
                         "time": time,
                         "length": round(length, 2),
                         "name": name,
                         "label": label,
                         "comment": comment}]
        except ValueError:
            return []

    def delete(self, name):
        return self.apply_label(name, 'delete')

