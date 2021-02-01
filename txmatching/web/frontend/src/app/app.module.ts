import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { LoginComponent } from './pages/login/login.component';
import { HomeComponent } from './pages/home/home.component';
import { HTTP_INTERCEPTORS, HttpClientModule } from '@angular/common/http';
import { ErrorInterceptor } from '@app/interceptors/error/error.interceptor';
import { AuthInterceptor } from '@app/interceptors/auth/auth.interceptor';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { AlertComponent } from './components/alert/alert.component';
import { ButtonComponent } from './components/button/button.component';
import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';
import { HeaderComponent } from './components/header/header.component';
import { DropdownComponent } from './components/dropdown/dropdown.component';
import { ConfigurationComponent } from './components/configuration/configuration.component';
import { LoadingComponent } from './components/loading/loading.component';
import { CountComponent } from './components/count/count.component';
import { ContainerComponent } from './components/container/container.component';
import { ContentComponent } from './components/content/content.component';
import { MatchingDetailComponent } from './components/matching-detail/matching-detail.component';
import { MatchingRoundComponent } from './components/matching-round/matching-round.component';
import { MatchingTransplantComponent } from './components/matching-transplant/matching-transplant.component';
import { CodeComponent } from './components/code/code.component';
import { FlagComponent } from './components/flag/flag.component';
import { MatchingItemComponent } from './components/matching-item/matching-item.component';
import { VarDirective } from './directives/ng-var/var.directive';
import { InfiniteScrollModule } from 'ngx-infinite-scroll';
import { LogoComponent } from './components/logo/logo.component';
import { AutocompleteLibModule } from 'angular-ng-autocomplete';
import { ConfigurationPatientsComponent } from './components/configuration-patients/configuration-patients.component';
import { MatChipsModule } from '@angular/material/chips';
import { MatAutocompleteModule } from '@angular/material/autocomplete';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatIconModule } from '@angular/material/icon';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { MatInputModule } from '@angular/material/input';
import { ConfigurationCountriesComponent } from './components/configuration-countries/configuration-countries.component';
import { ConfigurationScoresComponent } from './components/configuration-scores/configuration-scores.component';
import { MatSlideToggleModule } from '@angular/material/slide-toggle';
import { MatBadgeModule } from '@angular/material/badge';
import { PatientComponent } from './components/patient/patient.component';
import { CountryComponent } from './components/country/country.component';
import { PatientsComponent } from './pages/patients/patients.component';
import { ListItemComponent } from './components/list-item/list-item.component';
import { PatientPairItemComponent } from './components/patient-pair-item/patient-pair-item.component';
import { PatientPairDetailComponent } from './components/patient-pair-detail/patient-pair-detail.component';
import { ListItemDirective } from './directives/list-item/list-item.directive';
import { ListItemDetailDirective } from './directives/list-item-detail/list-item-detail.directive';
import { ItemComponent } from './components/list-item/item/item.component';
import { PatientPairComponent } from './components/patient-pair/patient-pair.component';
import { TabSwitchComponent } from './components/tab-switch/tab-switch.component';
import { AntibodiesComponent } from './components/patient-recipient-detail/antibodies/antibodies.component';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { AuthenticationComponent } from './pages/authentication/authentication.component';
import { ScoreIndicatorComponent } from './components/score-indicator/score-indicator.component';
import { PatientDonorItemComponent } from './components/patient-donor-item/patient-donor-item.component';
import { PatientDonorDetailComponent } from '@app/components/patient-donor-detail/patient-donor-detail.component';
import { PatientRecipientDetailComponent } from '@app/components/patient-recipient-detail/patient-recipient-detail.component';
import { PatientDonorDetailWrapperComponent } from '@app/components/patient-donor-detail-wrapper/patient-donor-detail-wrapper.component';
import { DonorTypeLabelPipe } from '@app/pipes/donor-type-label/donor-type-label.pipe';
import { AntibodyTitlePipe } from './pipes/antibody-title/antibody-title.pipe';
import { AbstractLoggedComponent } from './pages/abstract-logged/abstract-logged.component';
import { LoadingIconComponent } from './components/loading-icon/loading-icon.component';
import { MatListModule } from '@angular/material/list';

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
    ContainerComponent,
    ContentComponent,
    MatchingDetailComponent,
    MatchingRoundComponent,
    MatchingTransplantComponent,
    CodeComponent,
    FlagComponent,
    MatchingItemComponent,
    VarDirective,
    LogoComponent,
    ConfigurationPatientsComponent,
    ConfigurationCountriesComponent,
    ConfigurationScoresComponent,
    PatientComponent,
    CountryComponent,
    PatientsComponent,
    ListItemComponent,
    PatientPairItemComponent,
    PatientPairDetailComponent,
    ListItemDirective,
    ListItemDetailDirective,
    ItemComponent,
    PatientDonorDetailComponent,
    PatientRecipientDetailComponent,
    PatientPairComponent,
    TabSwitchComponent,
    AntibodiesComponent,
    AuthenticationComponent,
    ScoreIndicatorComponent,
    PatientDonorItemComponent,
    PatientDonorDetailWrapperComponent,
    DonorTypeLabelPipe,
    AntibodyTitlePipe,
    AbstractLoggedComponent,
    LoadingIconComponent
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    HttpClientModule,
    ReactiveFormsModule,
    FontAwesomeModule,
    InfiniteScrollModule,
    AutocompleteLibModule,
    FormsModule,
    MatChipsModule,
    MatAutocompleteModule,
    MatFormFieldModule,
    MatIconModule,
    BrowserAnimationsModule,
    MatInputModule,
    MatSlideToggleModule,
    MatBadgeModule,
    MatProgressSpinnerModule,
    MatListModule
  ],
  providers: [
    { provide: HTTP_INTERCEPTORS, useClass: AuthInterceptor, multi: true },
    { provide: HTTP_INTERCEPTORS, useClass: ErrorInterceptor, multi: true }
  ],
  bootstrap: [AppComponent]
})
export class AppModule { }
