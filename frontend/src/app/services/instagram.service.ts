import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { tap } from 'rxjs/operators';
import { BehaviorSubject, Observable, of } from 'rxjs';
import { Profile } from '../models/Profile';
import { Post } from '../models/Post';
import { InstagramComment } from '../models/IntagramComment';
import { InstagramMetrics } from '../models/InsgramMetrics';

export interface dataPost {
  skip: number;
  datas: Post[];
  userid: string;
}

@Injectable({
  providedIn: 'root',
})
export class InstagramService {
  private apiUrl = 'http://127.0.0.1:5000';

  private cache = new Map<string, any>();
  private cacheSubject = new BehaviorSubject<Map<string, any>>(new Map());

  constructor(private http: HttpClient) {}

  getProfiles(): Observable<Profile[]> {
    const cacheKey = 'profiles';
    if (this.cache.has(cacheKey)) {
      return of(this.cache.get(cacheKey));
    }
    return this.http
      .get<Profile[]>(`${this.apiUrl}/instagram/getprofiles`)
      .pipe(
        tap((profiles) => {
          this.cache.set(cacheKey, profiles);
          this.cacheSubject.next(new Map(this.cache));
        })
      );
  }

  getPosts(userid: string, skip: number, limit: number): Observable<Post[]> {
    const cacheKey = 'posts';
    if (this.cache.has(cacheKey)) {
      const posts = this.cache.get(cacheKey);
      if (posts) {
        const filteredPosts = posts.filter((data: dataPost) => {
          return data.userid == userid && data.skip == skip;
        });
        if (filteredPosts.length > 0) {
          return of(filteredPosts[0].datas);
        }
      }
    }
    let params = new HttpParams()
      .set('userid', userid)
      .set('skip', skip)
      .set('limit', limit);
    return this.http
      .get<Post[]>(`${this.apiUrl}/instagram/getposts`, { params })
      .pipe(
        tap((posts) => {
          const existingPosts = this.cache.has(cacheKey)
            ? this.cache.get(cacheKey)
            : [];
          const updatedPosts = [
            ...existingPosts,
            {
              skip: skip,
              userid: userid,
              datas: posts,
            },
          ];
          this.cache.set(cacheKey, updatedPosts);
          this.cacheSubject.next(new Map(this.cache));
        })
      );
  }

  getComments(mediaid: string): Observable<InstagramComment[]> {
    const cacheKey = 'comments';
    if (this.cache.has(cacheKey)) {
      const comments = this.cache.get(cacheKey);
      if (comments) {
        const filteredComments = comments.filter(
          (comment: InstagramComment) => comment.mediaid === mediaid
        );
        if (filteredComments.length > 0) {
          return of(filteredComments);
        }
      }
    }

    let params = new HttpParams().set('mediaid', mediaid);
    return this.http
      .get<InstagramComment[]>(`${this.apiUrl}/instagram/getcomments`, { params })
      .pipe(
        tap((data) => {
          const existingComments = this.cache.has(cacheKey)
            ? this.cache.get(cacheKey)
            : [];
          const updatedComments = [...existingComments, ...data];
          this.cache.set(cacheKey, updatedComments);
          this.cacheSubject.next(new Map(this.cache));
        })
      );
  }

  getMetrics(userid: string): Observable<InstagramMetrics> {
    const cacheKey = 'metrics';
    if (this.cache.has(cacheKey)) { 
      const metrics = this.cache.get(cacheKey);
      if (metrics) {
        const filteredPosts = metrics.filter((data: any) => {return data.userid == userid });
        if (filteredPosts.length > 0) {
          return of(filteredPosts);
        }
      }
    }
    let params = new HttpParams().set('userid', userid)
    return this.http
      .get<InstagramMetrics>(`${this.apiUrl}/instagram/getmetrics`, { params })
      .pipe(
        tap((metrics: InstagramMetrics) => {
          const existingMetrics = this.cache.has(cacheKey)
            ? this.cache.get(cacheKey)
            : [];
          const updatedMetrics = [...existingMetrics, metrics];
          this.cache.set(cacheKey, updatedMetrics);
          this.cacheSubject.next(new Map(this.cache));
        })
      );
  }
}
