import { Component, inject, Input, OnInit, ElementRef, ViewChild } from '@angular/core';
import { InstagramService } from '../../../services/instagram.service';
import { InstagramMetrics } from '../../../models/InsgramMetrics';
import { IconsModule } from '../../../icons.module';
import { Chart, registerables } from 'chart.js';
import { CommonModule } from '@angular/common';

Chart.register(...registerables);

interface GraphicData {
  data: any;
  type: 'bar' | 'line';
  title: string;
}


@Component({
  selector: 'app-instagram-metrics',
  standalone: true,
  imports: [IconsModule, CommonModule],
  templateUrl: './instagram-metrics.component.html',
  styleUrl: './instagram-metrics.component.css'
})
export class InstagramMetricsComponent implements OnInit {
  @ViewChild('myChartLikes', { static: true }) private chartLikesRef!: ElementRef;
  @ViewChild('myChartComments', { static: true }) private chartCommentsRef!: ElementRef;
  @ViewChild('myChartFollowers', { static: true }) private chartFollowersRef!: ElementRef;
  
  @Input() userid: string = ''


  metrics: InstagramMetrics = {
    userid: '',
    likesCount: 0,
    commentsCount: 0,
    lastPosts: [],
    interactions: 0,
    statistics: [],
  }

  private InstagramService = inject(InstagramService);
  

  ngOnInit(): void {
    this.InstagramService.getMetrics(this.userid).subscribe({
      next: (data: InstagramMetrics) => {
        this.metrics = data;
        console.log(this.metrics)
        this.renderChartLikes()
        this.renderChartComments()
        this.renderChartFollowers()
      },
      error: (error) => { 
        console.log(error)
        //console.error('Erro ao obter métricas do usuario', error); 
        //this.isLoadingChannel = false;
        //this.showChannel = false;
      }
    });
  }

  chartLikes!: Chart<'bar' | 'line'>;
  private renderChartLikes(): void {
    const data = {
      labels: this.metrics.statistics.map(statistic => {return statistic.date}).reverse(),
      datasets: [
        {
          label: 'Reações',
          data: this.metrics.statistics.map(statistic => {return statistic.likes}).reverse(),
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
      labels: this.metrics.statistics.map(statistic => {return statistic.date}).reverse(),
      datasets: [
        {
          label: 'Comentários',
          data: this.metrics.statistics.map(statistic => {return statistic.comments}).reverse(),
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
      labels: this.metrics.statistics.map(statistic => {return statistic.date}).reverse(),
      datasets: [
        {
          label: 'Seguidores',
          data: this.metrics.statistics.map(statistic => {return statistic.followers}).reverse(),
          backgroundColor: 'rgba(0,0,0,0.5)',
          fill: true,
          tension: 0.1,
        }
      ],
      type: 'line',
      title: 'Comentários em publicações',
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
}
