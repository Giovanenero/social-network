import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { CardVideoComponent } from '../../../components/cards/card-video/card-video.component';

import { Video } from '../../../models/Video';
import { YoutubeService } from '../../../services/youtube.service';

@Component({
  selector: 'app-videos',
  standalone: true,
  imports: [CardVideoComponent, CommonModule],
  templateUrl: './videos.component.html',
  styleUrl: './videos.component.css',
})
export class VideosComponent {
  videos: Video[] = [];
  isLoadingVideos: boolean = true;

  private youtubeService = inject(YoutubeService);

  ngOnInit(): void {
    this.getVideos();
  }

  getVideos(): void {
    this.youtubeService.getVideos().subscribe({
      next: (data: Video[]) => {
        this.videos = data.map((element) => {
          let date = new Date(element.publishedAt);
          let publishedAt = `${date.getDay()}/${date.getMonth()}/${date.getFullYear()}`;
          return {
            ...element,
            publishedAt: publishedAt
          };
        });
        this.isLoadingVideos = false;
      },
      error: (error) => {
        console.error('Erro ao obter dados do canal:', error);
        this.isLoadingVideos = false;
      }
    });
  }
}
