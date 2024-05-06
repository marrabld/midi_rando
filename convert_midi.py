import mido
from random import randint
import yaml

# Load configuration from YAML
with open('config.yaml', 'r') as file:
    config = yaml.safe_load(file)
    drum_channel = config['settings']['channel']
    kick_drum_note = config['settings']['note']
    randomness = config['settings']['randomness']
    bias_amount = config['bias']['amount']
    bias_frequency = config['bias']['frequency']

def list_midi_channels(file_path):
    mid = mido.MidiFile(file_path)
    channels = set()

    for track in mid.tracks:
        for msg in track:
            if hasattr(msg, 'channel'):
                channels.add(msg.channel)

    return sorted(list(channels))

def list_notes_in_channel(file_path, channel):
    mid = mido.MidiFile(file_path)
    notes = set()

    for track in mid.tracks:
        for msg in track:
            if hasattr(msg, 'note') and msg.channel == channel:
                notes.add(msg.note)

    return sorted(list(notes))

def randomize_kick_drum_velocity(file_path, output_path):
    mid = mido.MidiFile(file_path)
    new_mid = mido.MidiFile()

    note_count = 0  # Track the count of kick drum notes

    for track in mid.tracks:
        new_track = mido.MidiTrack()
        new_mid.tracks.append(new_track)
        for msg in track:
            if msg.type == 'note_on' and msg.channel == drum_channel and msg.note == kick_drum_note:
                # Base velocity determined randomly within specified randomness
                base_velocity = randint(64 - randomness, 64 + randomness)
                # Ensure base velocity is within 0-127 range
                base_velocity = max(0, min(127, base_velocity))

                # Apply bias based on the configuration
                if note_count % bias_frequency == 0:
                    base_velocity = min(base_velocity + bias_amount, 127)
                new_msg = msg.copy(velocity=base_velocity)
                new_track.append(new_msg)
                note_count += 1
            else:
                new_track.append(msg)

    new_mid.save(output_path)

# Example usage
midi_file_path = 'data/midi_rando.mid'

print("Channels in use:", list_midi_channels(midi_file_path))
print("Notes on drum channel:", list_notes_in_channel(midi_file_path, drum_channel))

randomize_kick_drum_velocity(midi_file_path, 'output_midi_file.mid')
