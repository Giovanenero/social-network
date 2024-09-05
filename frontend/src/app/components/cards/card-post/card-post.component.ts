import { Component, inject, Input, OnInit, Renderer2 } from '@angular/core';
import { Post } from '../../../models/Post';
import { CommonModule } from '@angular/common';
import { IconsModule } from '../../../icons.module';
import { DomSanitizer, SafeResourceUrl } from '@angular/platform-browser';
import { InstagramCommentsPopupComponent } from '../../../views/popups/instagram-comments-popup/instagram-comments-popup.component';

@Component({
  selector: 'app-card-post',
  standalone: true,
  imports: [CommonModule, IconsModule, InstagramCommentsPopupComponent],
  templateUrl: './card-post.component.html',
  styleUrl: './card-post.component.css',
})
export class CardPostComponent implements OnInit {
  @Input() post: Post = {
    mediaid: '',
    caption: '',
    date: '',
    likeCount: 0,
    isVideo: false,
    duration: 0,
    videoViewCount: 0,
    medias: [],
    commentCount: 0,
    extraction: '',
    userid: '',
  };

  mediaIterator: number = 0;
  showComments: boolean = false;
  private renderer: Renderer2 = inject(Renderer2);

  constructor(private sanitizer: DomSanitizer) {}

  ngOnInit(): void {
    console.log(this.post.caption.includes('\n') == true ? "sim" : 'nao')
  }

  getButtonClass(): string {
    if (this.post.commentCount > 0) {
      return 'button-active';
    }
    return 'button-inactive';
  }

  handleClickButton(isLeft: boolean): void {
    if (isLeft) {
      if (this.mediaIterator > 0) {
        this.mediaIterator--;
      }
    } else {
      if (this.mediaIterator < this.post.medias.length - 1) {
        this.mediaIterator++;
      }
    }

  }

  handleComments(): void {
    if(this.post.commentCount > 0){
      this.showComments = !this.showComments;
    }
  }

  getVideo(url: string): SafeResourceUrl {
    return  this.sanitizer.bypassSecurityTrustResourceUrl(this.post.medias[this.mediaIterator].url);
  }

  getDuration(duration: number): string {
    if(duration >= 3600){
      return Math.floor(duration / (3600)) + 'h'
    } else if(duration >= 60) {
      return Math.floor(duration / 60) + 'm' + Math.floor(duration % 60) + 's';
    }
    return duration.toFixed(0) + 's';
  }

  getDate(date: string): string {
    const format = new Date(date);
    return format.toLocaleDateString() + ' às ' + format.toLocaleTimeString();
  }
}
