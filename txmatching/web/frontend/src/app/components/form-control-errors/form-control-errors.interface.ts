export const errorMessages: { [key: string]: Function; } = {
  required: () => 'This field is required',
  minlength: (par: { requiredLength: number; }) => `Min ${par.requiredLength} chars is required`,
  invalidCountry: () => 'Choose one of existing countries'
};
