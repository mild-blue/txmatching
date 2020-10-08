import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { HomeComponent } from '@app/pages/home/home.component';
import { LoginComponent } from '@app/pages/login/login.component';
import { AuthGuard } from '@app/guards/auth/auth.guard';
import { PatientsComponent } from '@app/pages/patients/patients.component';
import { AuthenticationComponent } from '@app/pages/authentication/authentication.component';
import { OtpGuard } from '@app/guards/otp/otp.guard';
import { LoginGuard } from '@app/guards/login/login.guard';

const routes: Routes = [
  { path: 'matchings', component: HomeComponent, canActivate: [AuthGuard] },
  { path: 'patients', component: PatientsComponent, canActivate: [AuthGuard] },
  { path: 'login', component: LoginComponent, canActivate: [LoginGuard] },
  { path: 'authentication', component: AuthenticationComponent, canActivate: [OtpGuard] },

  // otherwise redirect to home
  { path: '', pathMatch: 'full', redirectTo: 'matchings' },
  { path: '**', redirectTo: '' }
];

@NgModule({
  imports: [RouterModule.forRoot(routes, { useHash: true })],
  exports: [RouterModule]
})
export class AppRoutingModule { }
