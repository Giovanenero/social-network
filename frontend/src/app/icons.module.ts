import { NgModule } from '@angular/core';
import { NgIconsModule } from '@ng-icons/core';
import {
  bootstrapYoutube,
  bootstrapFacebook,
  bootstrapInstagram,
  bootstrapHouseFill,
  bootstrapHandThumbsUp,
  bootstrapHandThumbsDown,
  bootstrapChatSquareDotsFill,
  bootstrapSearch,
  bootstrapShare,
  bootstrapEye,
  bootstrapDownload,
  bootstrapChatSquare,
  bootstrapPeople,
  bootstrapCameraVideo,
  bootstrapAward,
  bootstrapChevronDown,
  bootstrapChevronRight,
  bootstrapClock
} from '@ng-icons/bootstrap-icons';

@NgModule({
  imports: [
    NgIconsModule.withIcons({
      bootstrapYoutube,
      bootstrapFacebook,
      bootstrapInstagram,
      bootstrapHouseFill,
      bootstrapHandThumbsUp,
      bootstrapHandThumbsDown,
      bootstrapChatSquareDotsFill,
      bootstrapSearch,
      bootstrapShare,
      bootstrapEye,
      bootstrapDownload,
      bootstrapChatSquare,
      bootstrapPeople,
      bootstrapCameraVideo,
      bootstrapAward,
      bootstrapChevronDown,
      bootstrapChevronRight,
      bootstrapClock
    }),
  ],
  exports: [NgIconsModule],
})
export class IconsModule {}
