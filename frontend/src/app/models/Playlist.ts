export interface Playlist {
    playlistId?: string;
    channelId?: string;
    videosId: string[];
    title: string;
    description?: string;
    publishedAt: string;
    imgUrl?: string;
    extraction?: string;
  }
  