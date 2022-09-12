// eslint-disable-next-line @typescript-eslint/no-explicit-any
const isError = (candidate: any): candidate is Error => {
  return typeof candidate === "object" && "message" in candidate;
};

export const getErrorMessage = (error: unknown): string => {
  let message = "Něco se pokazilo, zkuste to prosím později.";

  if (isError(error)) {
    message = error.message;
  } else if (typeof error === "string") {
    message = error;
  } else {
    console.warn("Error has an unknown type. Showing generic message instead. Error:", error);
  }

  return message;
};
