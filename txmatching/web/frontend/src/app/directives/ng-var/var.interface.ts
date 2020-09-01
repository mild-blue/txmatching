export class VarDirectiveContext<T> {
  $implicit: T;
  ngVar: T;

  constructor(variable: T) {
    this.$implicit = this.ngVar = variable;
  }
}
