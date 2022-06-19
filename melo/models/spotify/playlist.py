from typing import Dict, List, Optional

from .track import PlaylistTrack
from .user import User
from ...utils import SPOTIFY, Image, URIBase

class Playlist(URIBase): #pylint: disable=too-many-instance-attributes
    '''A Spotify playlist object'''
    def __init__(self, data: Dict) -> None:

        self.id: str = data.get('id') #pylint: disable=invalid-name

        self.name: str = data.get('name')
        self.owner: User = User(data.get('owner'))
        self.snapshot_id: str = data.get('snapshot_id')
        self.href: str = 'https://open.spotify.com/playlist/' + self.id
        self.uri: str = data.get('uri')

        self.public: bool = data.get('public')
        self.collaborative: bool = data.get('collaborative')
        self.description: str = data.get('description')
        self.followers: int = data.get('followers', {}).get('total', 0)

        self.tracks: List[PlaylistTrack] = [
            PlaylistTrack(track) for track in data['tracks']['items']
        ] if 'items' in data['tracks'] else []

        self.images: List[Image] = [
            Image(**image_) for image_ in data.get('images', [])
        ]

        self.total_tracks: int = data.get('tracks')['total']

    def __repr__(self) -> str:
        return f"melo.Playlist - {(self.name or self.id or self.uri)!r}"

    def __str__(self) -> str:
        return str(self.id)

    def get_tracks(
        self,
        limit: Optional[int] = 20,
        offset: Optional[int] = 0
    ) -> List[PlaylistTrack]:
        '''Get  a list of tracks based on the given limit and offset

        Parameters
        ----------
        limit: `int`
            The maximum number of tracks to return.
        offset: `int`
            Specifies where the API should begin fetching tracks from.

        Returns
        -------
        result: `List[PlaylistTrack]`
            A list of tracks from the playlist.
        '''

        if (offset + limit) < self.total_tracks:
            return [PlaylistTrack(track_) for track_ in self.tracks[offset : offset + limit]]

        data = SPOTIFY.playlist_tracks(
            self.id,
            limit=limit,
            offset=offset 
        )

        return [PlaylistTrack(track_) for track_ in data['items']]

    def get_all_tracks(self) -> List[PlaylistTrack]:
        '''Get a list of all the tracks in aplaylist

        This operation might take long depending on the size of the playlist.
        '''

        if len(self.tracks) >= self.total_tracks:
            return self.tracks

        self.tracks = []
        offset = 0

        while len(self.tracks) < self.total_tracks:
            data = SPOTIFY.playlist_tracks(
                self.id,
                limit = 50,
                offset = offset
            )

            self.tracks.extend([PlaylistTrack(track_) for track_ in data])
            offset += 50

        self.total_tracks = len(self.tracks)
        return self.tracks

    #TODO - implement scopes and playlist modifications