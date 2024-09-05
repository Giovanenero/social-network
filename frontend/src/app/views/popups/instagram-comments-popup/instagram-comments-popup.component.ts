import { CommonModule } from '@angular/common';
import { Component, EventEmitter, inject, Input, OnInit, Output } from '@angular/core';
import { IconsModule } from '../../../icons.module';
import { InstagramComment } from '../../../models/IntagramComment';
import { InstagramService } from '../../../services/instagram.service';

interface Owner {
  url: string,
  username: string,
  description: string,
  date: string
}

@Component({
  selector: 'app-instagram-comments-popup',
  standalone: true,
  imports: [CommonModule, IconsModule],
  templateUrl: './instagram-comments-popup.component.html',
  styleUrl: './instagram-comments-popup.component.css'
})

export class InstagramCommentsPopupComponent implements OnInit {
  @Input() mediaid: string = '';
  @Input() useridOwner: string = '';

  @Output() close = new EventEmitter<void>();

  isLoading: boolean = true;
  comments: InstagramComment[] = []

  private instagramService = inject(InstagramService);

  ngOnInit(): void {
    this.getComments();
  }

  onClose() {
    this.close.emit();
  }

  getDate(date: string): string {
    let newDate = new Date(date)
    return newDate.toLocaleDateString() + ' às ' + newDate.toLocaleTimeString()
  }

  getComments(): void {
    this.instagramService.getComments(this.mediaid).subscribe({
      next: (data: InstagramComment[]) => { 
        this.comments = data; 
        this.isLoading = false;
      },
      error: (error) => { 
        console.error('Erro ao obter dados do canal:', error); 
        this.isLoading = false;
        //this.showChannel = false;
      },
    });
  }

  handleReply(commentId: string): void {

  }

}
