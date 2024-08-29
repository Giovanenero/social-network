export interface Video {
    videoId: string;
    channelId: string;
    description: string;
    title: string;
    publishedAt: string;
    imgUrl: string;
    viewCount: number;
    likeCount: number;
    dislikeCount: number;
    favoriteCount: number;
    commentCount: number;
    duration: string;
    extraction: string;
    tags: string[];
}