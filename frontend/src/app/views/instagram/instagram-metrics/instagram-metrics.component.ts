import { Component, inject, Input, OnInit, ElementRef, ViewChild, AfterViewInit } from '@angular/core';
import { InstagramService } from '../../../services/instagram.service';
import { InstagramMetrics } from '../../../models/InsgramMetrics';
import { IconsModule } from '../../../icons.module';
import { Chart, registerables } from 'chart.js';
import { CommonModule } from '@angular/common';

Chart.register(...registerables);

@Component({
  selector: 'app-instagram-metrics',
  standalone: true,
  imports: [IconsModule, CommonModule],
  templateUrl: './instagram-metrics.component.html',
  styleUrl: './instagram-metrics.component.css'
})
export class InstagramMetricsComponent implements AfterViewInit {
  @ViewChild('myChartLikes', { static: false }) private chartLikesRef!: ElementRef;
  @ViewChild('myChartComments', { static: false }) private chartCommentsRef!: ElementRef;
  @ViewChild('myChartFollowers', { static: false }) private chartFollowersRef!: ElementRef;
  
  @Input() userid: string = ''
  @Input() postsLength: number = 0
  metrics: InstagramMetrics = {
    userid: '',
    likesCount: 0,
    commentsCount: 0,
    videosCount: 0,
    viewsCount: 0,
    lastPosts: [],
    interactions: 0,
    statistics: [],
    nextPost: {}
  }
  private InstagramService = inject(InstagramService);
  isLoading: boolean = true
  
  ngAfterViewInit(): void {
    this.InstagramService.getMetrics(this.userid).subscribe({
      next: (data: InstagramMetrics) => {
        this.metrics = data;
        this.isLoading = false;
        setTimeout(() => {
          this.renderChartFollowers();
          if(this.metrics.lastPosts.length){
            this.renderChartLikes();
            this.renderChartComments();
          }
        }, 10)
      },
      error: (error) => { 
        console.log(error);
        this.isLoading = false;
      }
    });
  }

  chartLikes!: Chart<'bar' | 'line'>;
  private renderChartLikes(): void {
    const data = {
      labels: this.metrics.statistics.map(statistic => {return statistic.date}),
      datasets: [
        {
          label: 'Reações',
          data: this.metrics.statistics.map(statistic => {return statistic.likes}),
          backgroundColor: 'rgba(0,0,0,0.5)',
          fill: true,
          tension: 0.1,
        }
      ],
      type: 'line',
      title: 'Reações em publicações',
    }

    const canvas = this.chartLikesRef.nativeElement as HTMLCanvasElement;
    this.chartLikes = new Chart(canvas, {
      type: 'line',
      data: data,
      options: {
        responsive: true,
        plugins: {
          legend: {
            position: 'top',
          },
          title: {
            display: true,
            text: "Histórico de reações",
            align: 'start',
            font: {
              size: 20,
              weight: 'bold'
            }
          },
          tooltip: {
            callbacks: {
              label: function (context) {
                const label = context.dataset.label || '';
                const value = context.raw;
                return `${label}: ${value}`;
              },
            },
          },
        },
        scales: {
          x: {
            beginAtZero: true,
            ticks: {
              font: {
                size: 12,
                weight: 'bold',
              },
            },
          },
          y: {
            beginAtZero: true,
          },
        },
      },
    });
  }

  chartComments!: Chart<'bar' | 'line'>;
  private renderChartComments(): void {
    const data = {
      labels: this.metrics.statistics.map(statistic => {return statistic.date}),
      datasets: [
        {
          label: 'Comentários',
          data: this.metrics.statistics.map(statistic => {return statistic.comments}),
          backgroundColor: 'rgba(0,0,0,0.5)',
          fill: true,
          tension: 0.1,
        }
      ],
      type: 'line',
      title: 'Comentários em publicações',
    }

    const canvas = this.chartCommentsRef.nativeElement as HTMLCanvasElement;
    this.chartComments = new Chart(canvas, {
      type: 'line',
      data: data,
      options: {
        responsive: true,
        plugins: {
          legend: {
            position: 'top',
          },
          title: {
            display: true,
            text: "Histórico de comentários",
            align: 'start',
            font: {
              size: 20,
              weight: 'bold'
            }
          },
          tooltip: {
            callbacks: {
              label: function (context) {
                const label = context.dataset.label || '';
                const value = context.raw;
                return `${label}: ${value}`;
              },
            },
          },
        },
        scales: {
          x: {
            beginAtZero: true,
            ticks: {
              font: {
                size: 12,
                weight: 'bold',
              },
            },
          },
          y: {
            beginAtZero: true,
          },
        },
      },
    });
  }

  chartFollowers!: Chart<'bar' | 'line'>;
  private renderChartFollowers(): void {
    const data = {
      labels: this.metrics.statistics.map(statistic => {return statistic.date}),
      datasets: [
        {
          label: 'Seguidores',
          data: this.metrics.statistics.map(statistic => {return statistic.followers}),
          backgroundColor: 'rgba(0,0,0,0.5)',
          fill: true,
          tension: 0.1,
        }
      ],
      type: 'line',
      title: 'Histórico de seguidores',
    }

    const canvas = this.chartFollowersRef.nativeElement as HTMLCanvasElement;
    this.chartFollowers = new Chart(canvas, {
      type: 'line',
      data: data,
      options: {
        responsive: true,
        plugins: {
          legend: {
            position: 'top',
          },
          title: {
            display: true,
            text: "Histórico de Seguidores",
            align: 'start',
            font: {
              size: 20,
              weight: 'bold'
            }
          },
          tooltip: {
            callbacks: {
              label: function (context) {
                const label = context.dataset.label || '';
                const value = context.raw;
                return `${label}: ${value}`;
              },
            },
          },
        },
        scales: {
          x: {
            beginAtZero: true,
            ticks: {
              font: {
                size: 12,
                weight: 'bold',
              },
            },
          },
          y: {
            beginAtZero: true,
          },
        },
      },
    });
  }

  getDate(value: string): string {
    let date = new Date(value)
    return date.toLocaleDateString()
  }

  getAverageViews(): number {
    if(this.postsLength){
      return Math.round(this.metrics.viewsCount / this.postsLength);
    }
    return 0;
  }
}
