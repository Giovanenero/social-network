import { Component } from '@angular/core';
import { Router } from '@angular/router';

import { IconsModule } from '../../icons.module'; 

@Component({
  selector: 'app-header',
  standalone: true,
  imports: [IconsModule],
  templateUrl: './header.component.html',
  styleUrls: ['./header.component.css'],
})
export class HeaderComponent {

  constructor(private router: Router) {}

  handleClick(route: string): void {
    // Navega para a rota especificada
    this.router.navigate([route]);
  }
}
