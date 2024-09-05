import { CommonModule } from '@angular/common';
import { Component, inject, OnInit, Renderer2 } from '@angular/core';
import { InstagramService } from '../../services/instagram.service';
import { Profile } from '../../models/Profile';
import { CardPostComponent } from '../../components/cards/card-post/card-post.component';
import { Post } from '../../models/Post';
import { IconsModule } from '../../icons.module';
import { InstagramMetricsComponent } from './instagram-metrics/instagram-metrics.component';

@Component({
  selector: 'app-instagram',
  standalone: true,
  imports: [CommonModule, CardPostComponent, IconsModule, InstagramMetricsComponent],
  templateUrl: './instagram.component.html',
  styleUrl: './instagram.component.css',
})
export class InstagramComponent implements OnInit {

  isPost: boolean = true;
  indexs: number[] = [];
  totalPages: number = 0;
  selectedPage: number = 1;

  posts: Post[] = [];
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
  private limit: number = 12;

  ngOnInit(): void {
    this.getProfiles();
    this.getPosts();
  }

  getProfiles(): void {
    this.InstagramService.getProfiles().subscribe({
      next: (data: Profile[]) => { 
        this.profiles = data;
        this.selectedProfile = this.profiles[0]
        this.totalPages = Math.ceil(this.selectedProfile.mediacount / 12);
        this.indexs = []
        this.selectedPage = 1;
        for(let i = 0; i < this.totalPages && i < 9; i++){
          this.indexs.push(i + 1)
        }
        //this.isLoadingChannel = false;
      },
      error: (error) => { 
        console.error('Erro ao obter usuários do instagram:', error); 
        //this.isLoadingChannel = false;
        //this.showChannel = false;
      },
    });
  }

  getPosts(): void {
    this.InstagramService.getPosts(this.selectedProfile.userid, (this.selectedPage - 1) * this.limit, this.limit).subscribe({
      next: (posts: Post[]) => { 
        this.posts = posts;
        //this.selectedProfile = this.profiles[0]
        //onsole.log(this.selectedProfile)
        //this.isLoadingChannel = false;
      },
      error: (error) => { 
        console.error(`Erro ao obter posts do usuário ${this.selectedProfile.userid} do instagram:`, error); 
        //this.isLoadingChannel = false;
        //this.showChannel = false;
      },
    });
  }

  handleProfile(username: string): void {
    const profile: Profile | undefined = this.profiles.find((p: Profile) => p.username === username);
    this.selectedProfile = profile ? profile : this.profiles[0]
    const profileSection = document.querySelector('.section-profile');
    this.totalPages = Math.ceil(this.selectedProfile.mediacount / 12);
    this.indexs = []
    this.selectedPage = 1;
    for(let i = 0; i < this.totalPages && i < 9; i++){
      this.indexs.push(i + 1)
    }

    if(this.isPost){
      this.getPosts()
    }

    if (profileSection) {
      this.renderer.addClass(profileSection, 'animate-profile');
      setTimeout(() => {
        this.renderer.removeClass(profileSection, 'animate-profile');
      }, 500);
    }
  }

  handleClick(name: string): void {
    this.isPost = name === "posts"
  }

  handlePage(index: number): void {
    if(this.selectedPage != index){
      this.selectedPage = index;
      this.getPosts();
    }
  }

  handleNext(): void {
    if(this.selectedPage < this.totalPages){
      if(this.indexs[this.indexs.length - 1] == this.selectedPage){
        this.indexs.shift()
        this.indexs.push(this.selectedPage + 1);
      }
      this.selectedPage++;
      this.getPosts();
    }
  }

  handlePrev(): void {
    if(this.selectedPage > 1){
      if(this.indexs[0] == this.selectedPage){
        this.indexs.pop()
        this.indexs.unshift(this.selectedPage - 1);
      }
      this.selectedPage--;
      this.getPosts();
    }
  }

}
