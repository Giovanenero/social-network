import { Component, OnInit, inject, Input, Output, EventEmitter } from '@angular/core';
import { Comment } from '../../../models/Comment';
import { CommonModule } from '@angular/common';
import { IconsModule } from '../../../icons.module';
import { YoutubeService } from '../../../services/youtube.service';

@Component({
  selector: 'app-comments-popup',
  standalone: true,
  imports: [CommonModule, IconsModule],
  templateUrl: './comments-popup.component.html',
  styleUrls: ['./comments-popup.component.css'],
})
export class CommentsPopupComponent implements OnInit {
  @Input() videoId: string = '';

  @Output() close = new EventEmitter<void>();

  comments: Comment[] = [];

  showReply: boolean = false;

  isLoadingComments: boolean = true;

  private youtubeService = inject(YoutubeService);

  ngOnInit(): void {
    this.getComments();
  }

  onClose() {
    this.close.emit();
  }

  getComments(): void {
    console.log(this.videoId);
    this.youtubeService.getComments(this.videoId).subscribe({
      next: (data: Comment[]) => {
        this.comments = data.map(element => {
          let date = new Date(element.publishedAt)
          return {
            ...element,
            publishedAt: `${date.getDay()}/${date.getMonth()}/${date.getFullYear()}`,
            replies: element?.replies?.map(reply => {
              let dateRepy = new Date(reply.publishedAt)
              return {
                ...reply,
                publishedAt: `${dateRepy.getDay()}/${dateRepy.getMonth()}/${dateRepy.getFullYear()}`,
              }
            })
          }
        });
        this.isLoadingComments = false
      },
      error: (error) => {
        console.error('Erro ao obter dados do canal:', error);
        this.isLoadingComments = false;
      },
    });
  }

  handleReply(commentId: string): void {
    const comment = this.comments.find(c => c.commentId === commentId);
    if (comment) {
      comment.show = !comment.show;
    }
  }

  closePopup(): void {
    console.log('fechar popup!');
  }
}