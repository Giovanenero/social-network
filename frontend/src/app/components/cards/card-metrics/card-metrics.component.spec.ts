import { ComponentFixture, TestBed } from '@angular/core/testing';

import { CardMetricsComponent } from './card-metrics.component';

describe('CardMetricsComponent', () => {
  let component: CardMetricsComponent;
  let fixture: ComponentFixture<CardMetricsComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [CardMetricsComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(CardMetricsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
