import { Component, OnInit, ElementRef, ViewChild, Input } from '@angular/core';
import { Chart, registerables } from 'chart.js';

Chart.register(...registerables);

interface GraphicData {
  data: any;
  type: 'bar' | 'line';
  title: string;
}

@Component({
  selector: 'app-card-metrics',
  standalone: true,
  templateUrl: './card-metrics.component.html',
  styleUrls: ['./card-metrics.component.css'],
  imports: [],
})
export class CardMetricsComponent implements OnInit {
  @ViewChild('myChart', { static: true }) private chartRef!: ElementRef;

  @Input() graphic: GraphicData = {
    data: {},
    type: 'bar',
    title: ''
  };

  private chart!: Chart<'bar' | 'line'>;

  ngOnInit(): void {
    this.createChart();
  }

  private createChart(): void {
    const canvas = this.chartRef.nativeElement as HTMLCanvasElement;

    let labels = this.graphic.data.labels;

    this.chart = new Chart(canvas, {
      type: this.graphic.type,
      data: this.graphic.data,
      options: {
        responsive: true,
        plugins: {
          legend: {
            position: 'top',
          },
          title: {
            display: true,
            text: this.graphic.title,
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
              callback: function(value) {
                const stringValue = labels[value].toString()
                if (stringValue.length > 18) {
                  return stringValue.substring(0, 18) + '...';
                }
                return value;
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
