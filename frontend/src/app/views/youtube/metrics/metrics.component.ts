import { Component, inject, OnInit } from '@angular/core';
import { CardMetricsComponent } from '../../../components/cards/card-metrics/card-metrics.component';

import { YoutubeService } from '../../../services/youtube.service';
import { Video } from '../../../models/Video';
import { CommonModule } from '@angular/common';
import { Playlist } from '../../../models/Playlist';

interface GraphicData {
  data: any;
  type: 'bar' | 'line';
  title: string;
}

@Component({
  selector: 'app-metrics',
  standalone: true,
  imports: [CardMetricsComponent, CommonModule],
  templateUrl: './metrics.component.html',
  styleUrls: ['./metrics.component.css'],
})
export class MetricsComponent implements OnInit {
  private youtubeService = inject(YoutubeService);

  likesChart: GraphicData = {
    data: [],
    type: 'line',
    title: '',
  };
  viewsChart: GraphicData = {
    data: [],
    type: 'line',
    title: '',
  };
  commentsChart: GraphicData = {
    data: [],
    type: 'line',
    title: '',
  };

  playlists: Playlist[] = [];
  labels: string[] = [];
  isLoadingGraphics: boolean = true;
  isLoadingPlaylists: boolean = false;

  ngOnInit(): void {
    this.youtubeService.getVideos().subscribe({
      next: (data: Video[]) => {
        data = data.slice(0, 5);
        (this.labels = data.map((video) => {
          return video.title;
        })),
          this.getLikesChart(
            data.map((video) => {
              return video.likeCount;
            }),
            data.map((video) => {
              return video.dislikeCount;
            })
          );

        this.getViewsChart(
          data.map((video) => {
            return video.viewCount;
          })
        );

        this.getCommentsChart(
          data.map((video) => {
            return video.commentCount;
          })
        );
        this.isLoadingGraphics = false;
      },
      error: (error) => {
        console.error('Erro ao obter dados do canal:', error);
        this.isLoadingGraphics = false;
      },
    });

    this.youtubeService.getPlaylists().subscribe({
      next: (playlists: Playlist[]) => {
        this.playlists = playlists;
        this.isLoadingPlaylists = true;
      }, error: (error) => {
        console.error('Erro ao obter dados de playlists do canal:', error);
        this.isLoadingPlaylists = true;
      },
    })

  }

  getLikesChart(likes: number[], deslikes: number[]): void {
    if (
      likes.find((like) => {
        return like > 0;
      }) ||
      deslikes.find((deslike) => {
        return deslike > 0;
      })
    ) {
      this.likesChart = {
        data: {
          labels: this.labels,
          datasets: [
            {
              label: 'Curtidas',
              data: likes,
              backgroundColor: 'rgba(0,0,0,0.5)',
              fill: true,
              tension: 0.1,
            },
            {
              label: 'Descurtidas',
              data: deslikes,
              backgroundColor: '#ADD8E6',
              fill: true,
              tension: 0.1,
            },
          ],
        },
        type: 'line',
        title: 'Curtidas em vídeos',
      };
    }
  }

  getViewsChart(views: number[]): void {
    if (
      views.find((view) => {
        return view > 0;
      })
    ) {
      this.viewsChart = {
        data: {
          labels: this.labels,
          datasets: [
            {
              label: 'Visualizações',
              data: views,
              backgroundColor: 'rgba(0,0,0,0.5)',
              fill: true,
              tension: 0.1,
            },
          ],
        },
        type: 'line',
        title: 'Visualizações em vídeos',
      };
    }
  }

  getCommentsChart(comments: number[]): void {
    if (
      comments.find((comment) => {
        return comment > 0;
      })
    ) {
      this.commentsChart = {
        data: {
          labels: this.labels,
          datasets: {
            label: 'Comentários',
            data: comments,
            backgroundColor: 'rgba(0,0,0,0.5)',
            fill: true,
            tension: 0.1,
          },
        },
        type: 'line',
        title: 'Comentários em vídeos',
      };
    }
  }

  isObjectEmpty(obj: any): boolean {
    return Object.keys(obj).length === 0;
  }
}
