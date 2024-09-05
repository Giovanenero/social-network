import { ComponentFixture, TestBed } from '@angular/core/testing';

import { InstagramCommentsPopupComponent } from './instagram-comments-popup.component';

describe('InstagramCommentsPopupComponent', () => {
  let component: InstagramCommentsPopupComponent;
  let fixture: ComponentFixture<InstagramCommentsPopupComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [InstagramCommentsPopupComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(InstagramCommentsPopupComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
