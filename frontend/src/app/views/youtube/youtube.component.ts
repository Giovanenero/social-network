import { Component, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { VideosComponent } from './videos/videos.component';
import { MetricsComponent } from './metrics/metrics.component';
import { IconsModule } from '../../icons.module';

import { YoutubeService } from '../../services/youtube.service';
import { Channel } from '../../models/Channel';

@Component({
  selector: 'app-youtube',
  standalone: true,
  imports: [
    CommonModule,
    VideosComponent,
    MetricsComponent,
    IconsModule
  ],
  templateUrl: './youtube.component.html',
  styleUrls: ['./youtube.component.css'],
})
export class YoutubeComponent implements OnInit {
  value: string = 'videos';
  isLoadingChannel: boolean = true;
  showChannel: boolean = true;

  private youtubeService = inject(YoutubeService);

  channel: Channel = {
    channelId: '',
    title: '',
    description: '',
    publishedAt: '',
    imgUrl: '',
    country: '',
    customUrl: '',
    viewCount: 0,
    subscriberCount: 0,
    videoCount: 0,
    extraction: '',
  };

  ngOnInit(): void {
    this.getChannel();
  }

  handleClick(selectedValue: string) {
    this.value = selectedValue;
  }

  getChannel(): void {
    this.youtubeService.getChannel().subscribe({
      next: (data: Channel) => { 
        this.channel = data; 
        this.isLoadingChannel = false;
      },
      error: (error) => { 
        console.error('Erro ao obter dados do canal:', error); 
        this.isLoadingChannel = false;
        this.showChannel = false;
      },
    });
  }
}