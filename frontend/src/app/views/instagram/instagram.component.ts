import { CommonModule } from '@angular/common';
import { Component, inject, OnInit, Renderer2 } from '@angular/core';
import { InstagramService } from '../../services/instagram.service';
import { Profile } from '../../models/Profile';

@Component({
  selector: 'app-instagram',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './instagram.component.html',
  styleUrl: './instagram.component.css',
})
export class InstagramComponent implements OnInit {

  isPost: boolean = true;

  profiles: Profile[] = [];
  selectedProfile: Profile = {
    username: '',
    fullname: '',
    biography: '',
    externalUrl: '',
    followers: 0,
    followees: 0,
    mediacount: 0,
    userid: '',
    url: '',
    extraction: '',
  }

  private InstagramService = inject(InstagramService);
  private renderer: Renderer2 = inject(Renderer2);

  ngOnInit(): void {
    this.getProfiles();
  }

  getProfiles(): void {
    this.InstagramService.getProfiles().subscribe({
      next: (data: Profile[]) => { 
        this.profiles = data;
        this.selectedProfile = this.profiles[0]
        console.log(this.selectedProfile)
        //this.isLoadingChannel = false;
      },
      error: (error) => { 
        console.error('Erro ao obter usuários do instagram:', error); 
        //this.isLoadingChannel = false;
        //this.showChannel = false;
      },
    });
  }

  handleProfile(username: string): void {
    const profile: Profile | undefined = this.profiles.find((p: Profile) => p.username === username);
    this.selectedProfile = profile ? profile : this.profiles[0]
    const profileSection = document.querySelector('.section-profile');

    if (profileSection) {
      this.renderer.addClass(profileSection, 'animate-profile');
      setTimeout(() => {
        this.renderer.removeClass(profileSection, 'animate-profile');
      }, 500); // Tempo da animação em milissegundos
    }
  }

  handleClick(name: string): void {
    this.isPost = name === "posts"
  }

}
