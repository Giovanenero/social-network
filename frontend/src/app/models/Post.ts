export interface Post {
    mediaid: string;
    caption: string;
    date: string;
    likeCount: number;
    isVideo: boolean;
    duration: number;
    videoViewCount?: number;
    medias: any[];
    commentCount: number;
    extraction: string;
    userid: string;
  }
  