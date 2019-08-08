import os
import logging
from mutagen.flac import FLAC


class RecordingsInterface:
    def __init__(self, folder='recordings', file_name_prefix='autosave'):
        self.file_prefix = file_name_prefix
        self.folder = folder
        self.label = None

    def get_file_path_from_label(self, label, name):
        path = os.path.join('..', self.folder, label, name)
        logging.info(f'From label {label} and {name} got path {path}')
        return path

    @classmethod
    def update_comment(cls, audio, comment):
        '''
        Takes path to an FLACC file and comment string and adds Vorbis comment string
        '''
        audio["Comment"] = comment
        audio.save()
        if len(comment) > 20:
            logging.debug(f"Added '{comment[:20] + '...'} comment' ")
        else:
            logging.debug(f"Added '{comment}' comment")
        return True

    @classmethod
    def update_comment_from_label(cls, label, name, comment):
        '''
        Takes path to an FLACC file and comment string and adds Vorbis comment string
        '''
        path = cls.get_file_path_from_label(label, name)
        try:
            audio = FLAC(path)
        except FileNotFoundError as e:
            logging.error(e)
            return False
        cls.update_comment(audio, comment)
        return True

    @classmethod
    def update_comment_from_path(cls, path, comment):
        '''
        Takes path to an FLACC file and comment string and adds Vorbis comment string
        '''
        try:
            audio = FLAC(path)
        except FileNotFoundError as e:
            logging.error(e)
            return False
        cls.update_comment(audio, comment)
        return True

    @classmethod
    def get_comment(cls, label, name):
        '''
        Reads comment of FLAC file
        '''
        path = cls.get_file_path_from_label(label, name)
        audio = FLAC(path)
        return audio["Comment"][0]

    def apply_label(self, label, name, new_label):
        '''
        Move a file from one folder to another. This acts as a pseudo persistent label without having to
        modify comments or metadata. Having all the 'sleeptalking' and 'not sleeptalking' files in their
        respective folders also makes it easier to train models
        :param old_label:
        :param new_label:
        :param name:
        :return:
        '''
        # Make sure we have that file, else send a 404
        try:
            # Move to label named folder
            current_path = os.path.join(self.folder, label, name)
            new_path = os.path.join(self.folder, new_label, name)
            os.rename(current_path, new_path)
            logging.debug(f'Moved file from {current_path} to {new_path}')
            return "Successfully moved file", 200
        except FileNotFoundError:
            # Send a 404 reponse back
            return "File not found", 404

    @staticmethod
    def get_all_sorted_file_paths():
        prefix_dir = 'recordings'
        autosave_dir = os.path.join(prefix_dir, 'autosave')
        is_sleeptalking_dir = os.path.join(prefix_dir, 'is-sleeptalking')
        not_sleeptalking_dir = os.path.join(prefix_dir, 'not-sleeptalking')
        all_file_paths = [os.path.join(autosave_dir, file_name) for file_name in os.listdir(autosave_dir)]
        all_file_paths.extend(
            [os.path.join(is_sleeptalking_dir, file_name) for file_name in os.listdir(is_sleeptalking_dir)])
        all_file_paths.extend(
            [os.path.join(not_sleeptalking_dir, file_name) for file_name in os.listdir(not_sleeptalking_dir)])
        logging.debug(f'Got {len(all_file_paths)} file paths')
        all_file_paths.sort(key=lambda x: os.path.getmtime(x))
        return all_file_paths

    @staticmethod
    def get_file_info_by_path(path):
        try:
            date, time = path.split("_")[1:3]
            time = time.replace(".flac", "")
            time = time.replace("-", ":")[0:5]
            label, name = os.path.split(path)
            label = os.path.split(label)[1]
            if path.endswith(".flac"):
                f = FLAC(path)
                length = f.info.length
                return [{"date": date,
                          "time": time,
                          "length": round(length, 2),
                          "name": name,
                          "label": label}]
        except ValueError:
            return []

    def delete(self, label, name):
        return self.apply_label('delete', label, name)

