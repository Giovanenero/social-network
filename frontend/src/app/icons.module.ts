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
  bootstrapChevronLeft,
  bootstrapClock,
  bootstrapHeart
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
      bootstrapChevronLeft,
      bootstrapClock,
      bootstrapHeart
    }),
  ],
  exports: [NgIconsModule],
})
export class IconsModule {}
