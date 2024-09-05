export interface InstagramComment {
    commentId: string;
    text: string;
    date: string;
    likesCount: number;
    username: string;
    url: string;
    replies: any[];
    extraction: string;
    mediaid: string;
    show?: boolean
}