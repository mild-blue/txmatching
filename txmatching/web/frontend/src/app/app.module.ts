import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { LoginComponent } from './pages/login/login.component';
import { HomeComponent } from './pages/home/home.component';
import { HTTP_INTERCEPTORS, HttpClientModule } from '@angular/common/http';
import { ErrorInterceptor } from '@app/interceptors/error/error.interceptor';
import { AuthInterceptor } from '@app/interceptors/auth/auth.interceptor';
import { ReactiveFormsModule } from '@angular/forms';
import { AlertComponent } from './components/alert/alert.component';
import { ButtonComponent } from './components/button/button.component';
import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';
import { HeaderComponent } from './components/header/header.component';
import { DropdownComponent } from './components/dropdown/dropdown.component';
import { ConfigurationComponent } from './components/configuration/configuration.component';
import { LoadingComponent } from './components/loading/loading.component';
import { CountComponent } from './components/count/count.component';
import { MatchingsExplorerComponent } from './components/matchings-explorer/matchings-explorer.component';
import { ContainerComponent } from './components/container/container.component';
import { ContentComponent } from './components/content/content.component';
import { MatchingDetailComponent } from './components/matching-detail/matching-detail.component';
import { MatchingRoundComponent } from './components/matching-round/matching-round.component';
import { MatchingTransplantComponent } from './components/matching-transplant/matching-transplant.component';
import { CodeComponent } from './components/code/code.component';
import { FlagComponent } from './components/flag/flag.component';

@NgModule({
  declarations: [
    AppComponent,
    LoginComponent,
    HomeComponent,
    AlertComponent,
    ButtonComponent,
    HeaderComponent,
    DropdownComponent,
    ConfigurationComponent,
    LoadingComponent,
    CountComponent,
    MatchingsExplorerComponent,
    ContainerComponent,
    ContentComponent,
    MatchingDetailComponent,
    MatchingRoundComponent,
    MatchingTransplantComponent,
    CodeComponent,
    FlagComponent
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    HttpClientModule,
    ReactiveFormsModule,
    FontAwesomeModule
  ],
  providers: [
    { provide: HTTP_INTERCEPTORS, useClass: AuthInterceptor, multi: true },
    { provide: HTTP_INTERCEPTORS, useClass: ErrorInterceptor, multi: true }

  ],
  bootstrap: [AppComponent]
})
export class AppModule { }
