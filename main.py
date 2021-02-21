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
        start *= 1000
        end *= 1000

        if start < segment_len and end <= segment_len:
            segment.append(audio_segment[start:end])

    return segment


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

    joined_bee_segments = join_segments(bee_segment)
    joined_nobee_segments = join_segments(nobee_segment)

    return joined_bee_segments, joined_nobee_segments


def save_segment(name, segment, folder_path, folder_type):
    path = os.path.join(folder_path, 'split_files', folder_type, name)
    print(f'Saving in - {path}')
    segment.export(path, format='wav')


def split_audio_by_type():
    audio_filenames, lab_filenames = load_filenames(MISSING_QUEEN_PATH)
    lab_paths = generate_lab_paths(lab_filenames, MISSING_QUEEN_PATH)

    for i, lab_path in enumerate(lab_paths):
        data = open_lab_file(lab_path)
        bee, nobee = organize_file_data(data)

        bee_segment, nobee_segment = split_audio_file(audio_filenames[i], bee, nobee, MISSING_QUEEN_PATH)

        save_segment(f'{i}.wav', bee_segment, MISSING_QUEEN_PATH, 'bee')
        save_segment(f'{i}.wav', nobee_segment, MISSING_QUEEN_PATH, 'nobee')


def get_audio_files_list(path):
    audio_files = list()

    for _, _, filenames in os.walk(path):
        audio_files = filenames
        break

    print(audio_files)

    return audio_files


def open_audio_files(path, audio_files):
    segments = list()

    for audio_file in audio_files:
        segments.append(AudioSegment.from_wav(os.path.join(path, audio_file)))

    print(segments)

    return segments


def main():
    bee_files_path = os.path.join(MISSING_QUEEN_PATH, 'split_files', 'bee')
    nobee_files_path = os.path.join(MISSING_QUEEN_PATH, 'split_files', 'nobee')

    bee_audio_files = get_audio_files_list(bee_files_path)
    bee_segments = open_audio_files(bee_files_path, bee_audio_files)
    bee_combined_segments = join_segments(bee_segments)
    print(len(bee_combined_segments))
    save_segment('missing_queenbee_bee.wav', bee_combined_segments, MISSING_QUEEN_PATH, 'full')

    # nobee_audio_files = get_audio_files_list(nobee_files_path)
    # nobee_segments = open_audio_files(nobee_files_path, nobee_audio_files)
    # nobee_combined_segments = join_segments(nobee_segments)
    # save_segment('missing_queenbee_nobee.wav', nobee_combined_segments, MISSING_QUEEN_PATH, 'full')


if __name__ == '__main__':
    main()
    # audio_filenames, lab_filenames = load_filenames(MISSING_QUEEN_PATH)
    # print(audio_filenames)
    # print(lab_filenames)
    # lab_paths = generate_lab_paths(lab_filenames, MISSING_QUEEN_PATH)
    # print(lab_paths)
    # data = open_lab_file(lab_paths[0])
    # print(data)
    # bee, nobee = organize_file_data(data)
    # print(bee)
    # print(nobee)
    # bee_path = os.path.join('split_files', 'bee')
    # nobee_path = os.path.join('split_files', 'nobee')
    # bee_segment, nobee_segment = split_audio_file(audio_filenames[0], bee, nobee, MISSING_QUEEN_PATH)
    #
    # print(bee_segment)
    # print(nobee_segment)
    #
    # save_segment('1.wav', bee_segment, MISSING_QUEEN_PATH, 'bee')
    # save_segment('1.wav', nobee_segment, MISSING_QUEEN_PATH, 'nobee')
