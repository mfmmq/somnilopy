from mutagen.id3 import ID3, COMM
from mutagen.aiff import AIFF
from soundfile import read as sf_read
from soundfile import write as sf_write
import os
import logging

def wav2aiff(wav_path, aiff_path=None, inplace=True):
	'''
	Converts wav file to aiff file

	If aiff_path is left unspecified, original wav name is used in same directory
	'''
	if not aiff_path:
		fn = wav_path.split('/')[-1].split('.')[0] # strips dirs and .wav from path
		aiff_path = '/'.join(wav_path.split('/')[:-1] + [fn + '.aiff']) # create aiff file path
	sf_write(aiff_path, *sf_read(wav_path))
	logging.info(f"{wav_path} converted to {aiff_path}") # TODO: change this to names rather than paths to be less verbose?
	if inplace:
		os.remove(wav_path)
		logging.info(f"{wav_path} deleted")

def add_aiff_comment(path, comment):
	'''
	Takes path to an AIFF file and comment string and adds the comment string to ID3 tags in file
	'''
	audio = AIFF(path)
	if not audio.tags:
		audio.add_tags()
	audio.tags["COMM"] = COMM(encoding=3, lang=u'eng', desc='desc', text=str(comment))
	audio.save()
	if len(comment) > 20:
		logging.info(f"Added '{comment[:20] + '...'}' comment to {path}")
	else:
		logging.info(f"Added '{comment}' comment to {path}")

def get_aiff_comment(path):
	'''
	Reads comment of AIFF file
	'''
	audio = AIFF(path)
	return audio.tags['COMM:desc:eng'].text[0]