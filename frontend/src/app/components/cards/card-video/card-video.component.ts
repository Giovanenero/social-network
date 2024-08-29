import { Component, Input, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { YouTubePlayerModule } from '@angular/youtube-player';
import { IconsModule } from './../../../icons.module'; 
import { CommentsPopupComponent } from '../../../views/popups/comments-popup/comments-popup.component';
import { Video } from "../../../models/Video";

@Component({
  selector: 'app-card-video',
  standalone: true,
  imports: [
    CommonModule, 
    IconsModule, 
    YouTubePlayerModule,
    CommentsPopupComponent
  ], 
  templateUrl: './card-video.component.html',
  styleUrls: ['./card-video.component.css'],
})

export class CardVideoComponent {
  @Input() video: Video = {
    videoId: '',
    channelId: '',
    description: '',
    title: '',
    publishedAt: '',
    imgUrl: '',
    viewCount: 0,
    likeCount: 0,
    dislikeCount: 0,
    favoriteCount: 0,
    commentCount: 0,
    duration: '',
    extraction: '',
    tags: []  
  };

  showComments : boolean = false;

  constructor() {}

  getDuration(duration: string): string {
    duration = duration.substring(2);

    const minMatch = duration.match(/(\d+)M/);
    const segMatch = duration.match(/(\d+)S/);

    const min = minMatch ? parseInt(minMatch[1], 10) : 0;
    const seg = segMatch ? parseInt(segMatch[1], 10) : 0;
    const totalSeg = (min * 60) + seg;

    if(totalSeg >= 3600){
      return Math.floor(totalSeg / 3600) + 'h';
    } else if(totalSeg >= 60){
      const m = Math.floor(totalSeg / 60);
      const s = totalSeg % 60;
      return m + 'm' + s + 's'
    }
    return totalSeg + 's'
  }

  getViews(view : number): string {
    if(view >= 1000){
      const mil = (view / 1000).toFixed(1).toString();
      if(mil.includes('.0')){
        return mil.substring(0, mil.indexOf('.0')) + 'mil';
      }
      return mil + 'mil'; 
    }
    return view.toString();
  }

  handleComments(): void {
    if(this.video.commentCount > 0){
      this.showComments = !this.showComments;
    }
  }

  getButtonClass(): string {
    if(this.video.commentCount > 0){
      return 'button-active';
    }
    return 'button-inactive';
  }
}