import { Directive, Input, TemplateRef, ViewContainerRef } from '@angular/core';
import { VarDirectiveContext } from '@app/directives/ng-var/var.interface';

@Directive({
  selector: '[ngVar]'
})
export class VarDirective {

  constructor(private _vcRef: ViewContainerRef,
              private _templateRef: TemplateRef<unknown>) {
  }

  @Input()
  set ngVar(variable: unknown) {
    const context = new VarDirectiveContext<typeof variable>(variable);
    this.updateView(context);
  }

  updateView(context: VarDirectiveContext<unknown>) {
    this._vcRef.clear();
    this._vcRef.createEmbeddedView(this._templateRef, context);
  }
}
