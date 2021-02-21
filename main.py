import os

import numpy as np
import librosa

from pydub import AudioSegment

MISSING_QUEEN_PATH = 'MissingQueen'
NORMAL_PATH = 'Normal'
NORMAL_QUEEN_PATH = 'NormalQueenBee'


def load_filenames(path):
    audio_filenames = list()

    for dirpath, dirnames, filenames in os.walk(path):
        audio_filenames.extend(filenames)
        break

    lab_filenames = list()
    for audio_filename in audio_filenames:
        lab_filenames.append(audio_filename[:-4] + '.lab')

    return audio_filenames, lab_filenames


def generate_lab_paths(lab_filenames, path):
    new_path = os.path.join(path, 'labels')
    lab_paths = list()
    for lab_filename in lab_filenames:
        lab_paths.append(os.path.join(new_path, lab_filename))

    return lab_paths


def open_lab_file(lab_filepath):
    with open(lab_filepath, 'r') as fp:
        data = fp.readlines()

    return data


def organize_file_data(raw_data):
    data = raw_data[1:]
    for i in range(len(data)):
        data[i] = data[i][:-1]

    bee = list()
    nobee = list()
    for i in range(len(data)):
        entry = data[i].split('\t')

        if entry[-1] == 'bee':
            bee.append((float(entry[0]), float(entry[1])))
        elif entry[-1] == 'nobee':
            nobee.append((float(entry[0]), float(entry[1])))

    return bee, nobee


def generate_segment_by_type(audio_segment, segment_len, type_durations):
    segment = list()

    for durations in type_durations:
        start, end = durations

        segment.append(audio_segment[start: end])

    return segment


def generate_individual_segments(audio_segment, segment_len, bees, nobees):
    bee_segment = AudioSegment.empty()
    nobee_segment = AudioSegment.empty()

    for d in bees:
        start, end = d

        if start < segment_len and end < segment_len:
            bee_segment += audio_segment[start:end]

    for d in nobees:
        start, end = d

        if start < segment_len and end < segment_len:
            nobee_segment += audio_segment[start:end]

    print(f'Bee {len(bee_segment)}')
    print(f'No Bee {len(nobee_segment)}')

    return bee_segment, nobee_segment


def join_segments(segments_list):
    combined_segment = AudioSegment.empty()

    for segment in segments_list:
        combined_segment += segment

    return combined_segment


def split_audio_file(audio_filename, bees, nobees, folder_path):
    audio_segment = AudioSegment.from_wav(os.path.join(folder_path, audio_filename))
    segment_len = len(audio_segment)

    bee_segment = generate_segment_by_type(audio_segment, segment_len, bees)
    nobee_segment = generate_segment_by_type(audio_segment, segment_len, nobees)

    generate_individual_segments(audio_segment, segment_len, bees, nobees)

    joined_bee_segments = join_segments(bee_segment)
    joined_nobee_segments = join_segments(nobee_segment)

    print(len(joined_bee_segments))
    print(len(joined_nobee_segments))

    bee_path = os.path.join(MISSING_QUEEN_PATH, 'split_files', 'bee', '1.wav')
    nobee_path = os.path.join(MISSING_QUEEN_PATH, 'split_files', 'nobee', '1.wav')

    joined_bee_segments.export(bee_path, format='wav')
    joined_nobee_segments.export(nobee_path, format='wav')

    return joined_bee_segments, joined_nobee_segments


def save_segment(name, segment, folder_path, folder_type):
    path = os.path.join(folder_path, 'split_files', folder_type, name)
    segment.export(path, format='wav')


if __name__ == '__main__':
    audio_filenames, lab_filenames = load_filenames(MISSING_QUEEN_PATH)
    print(audio_filenames)
    print(lab_filenames)
    lab_paths = generate_lab_paths(lab_filenames, MISSING_QUEEN_PATH)
    print(lab_paths)
    data = open_lab_file(lab_paths[0])
    print(data)
    bee, nobee = organize_file_data(data)
    print(bee)
    print(nobee)
    bee_path = os.path.join('split_files', 'bee')
    nobee_path = os.path.join('split_files', 'nobee')
    bee_segment, nobee_segment = split_audio_file(audio_filenames[0], bee, nobee, MISSING_QUEEN_PATH)

    print(bee_segment)
    print(nobee_segment)

    # save_segment('1.wav', bee_segment, MISSING_QUEEN_PATH, 'bee')
    # save_segment('1.wav', nobee_segment, MISSING_QUEEN_PATH, 'nobee')
