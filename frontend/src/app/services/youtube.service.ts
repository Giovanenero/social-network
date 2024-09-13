import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { tap } from 'rxjs/operators';
import { BehaviorSubject, Observable, of } from 'rxjs';
import { Channel } from '../models/Channel';
import { Video } from '../models/Video';
import { Comment } from '../models/Comment';
import { Playlist } from '../models/Playlist';

@Injectable({
  providedIn: 'root'
})

export class YoutubeService {

  private apiUrl = 'http://127.0.0.1:5000';
  //private apiUrl = 'http://backend:5000';

  private channelId = "UCaldTW0ntt8_XOvllDpI0Dw";
  //private channelId = "UCUa8BOx2F3hlxgPcpZmnBnQ";

  private cache = new Map<string, any>();
  private cacheSubject = new BehaviorSubject<Map<string, any>>(new Map());

  constructor(private http: HttpClient) {}

  getChannel(): Observable<Channel> {
    const cacheKey = "channel"
    if(this.cache.has(cacheKey)){
      return of(this.cache.get(cacheKey))
    }
    let params = new HttpParams().set('channelId', this.channelId);
    return this.http.get<Channel>(`${this.apiUrl}/youtube/getchannel`, { params }).pipe(
      tap(channel => {
        this.cache.set(cacheKey, channel);
        this.cacheSubject.next(new Map(this.cache));
      })
    )
  }

  getVideos(): Observable<Video[]> {
    const cacheKey = "videos";
    if(this.cache.has(cacheKey)){
      return of(this.cache.get(cacheKey));
    }
    let params = new HttpParams().set('channelId', this.channelId);
    return this.http.get<Video[]>(`${this.apiUrl}/youtube/getvideos`, { params }).pipe(
      tap(videos => {
        this.cache.set(cacheKey, videos);
        this.cacheSubject.next(new Map(this.cache))
      })
    );
  }

  getComments(videoId: string): Observable<Comment[]> {
    const cacheKey = "comments";
    if(this.cache.has(cacheKey)){
      const comments = this.cache.get(cacheKey);
      if (comments) {
        const filteredComments = comments.filter((comment : Comment) => comment.videoId === videoId);
        if (filteredComments.length > 0) {
          return of(filteredComments);
        }
      }
    }

    let params = new HttpParams().set('videoId', videoId);
    return this.http.get<Comment[]>(`${this.apiUrl}/youtube/getcomments`, { params }).pipe(
      tap(data => {
        const existingComments = this.cache.has(cacheKey) ? this.cache.get(cacheKey) : [];
        const updatedComments = [...existingComments, ...data];
        this.cache.set(cacheKey, updatedComments);
        this.cacheSubject.next(new Map(this.cache))
      })  
    )
  }

  getPlaylists(): Observable<Playlist[]> {
    const cacheKey = "playlists";
    if(this.cache.has(cacheKey)){
      return of(this.cache.get(cacheKey));
    }
    let params = new HttpParams().set('channelId', this.channelId);
    return this.http.get<Playlist[]>(`${this.apiUrl}/youtube/getplaylists`, { params }).pipe(
      tap(playlists => {
        this.cache.set(cacheKey, playlists);
        this.cacheSubject.next(new Map(this.cache))
      })
    );
  }
}
