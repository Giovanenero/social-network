import { ComponentFixture, TestBed } from '@angular/core/testing';

import { CardVideoComponent } from './card-video.component';

describe('CardVideoComponent', () => {
  let component: CardVideoComponent;
  let fixture: ComponentFixture<CardVideoComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [CardVideoComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(CardVideoComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
