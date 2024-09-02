import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { tap } from 'rxjs/operators';
import { BehaviorSubject, Observable, of } from 'rxjs';
import { Profile } from '../models/Profile';

@Injectable({
  providedIn: 'root'
})
export class InstagramService {

  private apiUrl = 'http://127.0.0.1:5000';

  private cache = new Map<string, any>();
  private cacheSubject = new BehaviorSubject<Map<string, any>>(new Map());

  constructor(private http: HttpClient) {}

  getProfiles(): Observable<Profile[]> {
    const cacheKey = "profiles"
    if(this.cache.has(cacheKey)){
      return of(this.cache.get(cacheKey))
    }
    return this.http.get<Profile[]>(`${this.apiUrl}/instagram/getprofiles`).pipe(
      tap(profiles => {
        this.cache.set(cacheKey, profiles);
        this.cacheSubject.next(new Map(this.cache));
      })
    )
  }
}
