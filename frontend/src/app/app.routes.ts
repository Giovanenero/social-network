import { Routes } from '@angular/router';
import { DashboardComponent } from './views/dashboard/dashboard.component';
import { YoutubeComponent } from './views/youtube/youtube.component';
import { FacebookComponent } from './views/facebook/facebook.component';
import { InstagramComponent } from './views/instagram/instagram.component';

export const routes: Routes = [
    {path: '', component: DashboardComponent},
    {path: 'youtube', component: YoutubeComponent},
    {path: 'facebook', component: FacebookComponent},
    {path: 'instagram', component: InstagramComponent},
];
