export interface Comment {
    commentId: string;
    videoId: string;
    channelId: string;
    textOriginal: string;
    authorProfileImageUrl: string;
    likeCount: number;
    dislikeCount: number;
    publishedAt: string;
    authorDisplayName: string;
    extraction: string;
    show?: boolean;
    replies: Comment[];
}