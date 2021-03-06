#!/usr/bin/env python3

from functools import reduce
from . import gazelle_api


def get_matching_torrent_from_group(torrent_group, local_release):
    for torrent in torrent_group["torrent"]:
        is_on_tracker = compare_release_from_tracker(torrent, local_release)
        if is_on_tracker:
            return torrent


def compare_release_from_tracker(tracker_torrent, local_release):
    # Considers that our release is uniformely tagged, so the 1st item
    # represent the all album
    local_item = local_release.items[0]

    if tracker_torrent["format"] == "MP3":
        same_format = compare_lossy_format(tracker_torrent, local_release)
    else:
        same_format = compare_lossless_format(tracker_torrent, local_release)
    if not same_format:
        return False

    same_version = True
    if local_item.albumdisambig:
        same_version = (
            local_item.albumdisambig.lower() in
            tracker_torrent["remasterTitle"].lower()
        )
    if not same_version:
        return False

    return True


def compare_lossy_format(tracker_torrent, local_release):
    local_format = local_release.items[0].format
    if tracker_torrent["format"].lower() != local_format.lower():
        return False

    average_local_bitrate = get_average_bitrate(local_release)

    return tracker_torrent["encoding"] == (
        gazelle_api.numeric_bitrate_to_gazelle_bitrate(average_local_bitrate)
    )


def get_average_bitrate(local_release):
    bitrates = [i.bitrate for i in local_release.items]
    return reduce(lambda x, y: x + y, bitrates) / len(bitrates)


def compare_lossless_format(tracker_torrent, local_release):
    local_format = local_release.items[0].format
    if tracker_torrent["format"].lower() != local_format.lower():
        return False

    if tracker_torrent["format"] == "FLAC 24bit":
        return local_format.bitdepth == 24

    return True
