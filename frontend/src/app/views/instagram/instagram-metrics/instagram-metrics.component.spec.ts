import { ComponentFixture, TestBed } from '@angular/core/testing';

import { InstagramMetricsComponent } from './instagram-metrics.component';

describe('InstagramMetricsComponent', () => {
  let component: InstagramMetricsComponent;
  let fixture: ComponentFixture<InstagramMetricsComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [InstagramMetricsComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(InstagramMetricsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
