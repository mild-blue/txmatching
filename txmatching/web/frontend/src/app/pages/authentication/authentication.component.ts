import { Component, OnInit } from '@angular/core';
import { FormControl, FormGroup, Validators } from '@angular/forms';

@Component({
  selector: 'app-authentication',
  templateUrl: './authentication.component.html',
  styleUrls: ['./authentication.component.scss']
})
export class AuthenticationComponent implements OnInit {

  public form: FormGroup = new FormGroup({
    input: new FormControl([''], Validators.required)
  });

  constructor() {
  }

  ngOnInit(): void {
  }

  public onSubmit(): void {

    console.log(this.form.valid, this.form.value);
  }

}
