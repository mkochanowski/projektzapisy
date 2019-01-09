import renderMathInElement from "katex/dist/contrib/auto-render";
// import { whenDomLoaded } from "common/utils";

type UnconstrainedFunction = (...args: any[]) => any;
export function whenDomLoaded(fn: UnconstrainedFunction): void {
   if (document.readyState !== "loading") {
      fn();
   } else {
      window.addEventListener("DOMContentLoaded", fn);
   }
}

whenDomLoaded(() => {
   const element = document.getElementById("od-vote-main-rules")!;
   renderMathInElement(element);
});
