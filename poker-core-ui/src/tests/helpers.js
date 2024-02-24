// When you want to resolve / reject a promise, but not immediately
// This allows for a less clunky way of doing this:

// let resolveFunction
// let rejectFunction
// const promise = new Promise((resolve, reject) => {
//   resolveFunction = resolve
//   rejectFunction = reject
// }
// [do some stuff]
// resolveFunction() / rejectFunction()

// by doing this instead:

// const later = new Later()
// [do some stuff]
// later.resolve(true) / later.reject(false)

// An example use-case for this: 
// Let's say you sibmit a form, and you want to disable the submit button until the request is complete.
// In your tests, you will most likely want to mock the promise, but if you resolve immediately, 
// you won't be able to test the disabled state of the button.

class Later extends Promise {
    constructor(def = (res, rej)=>{}) {
      let res, rej;
      super((resolve, reject)=>{
        def(resolve, reject);
        res = resolve;
        rej = reject;
      });
      this.resolve = res;
      this.reject = rej;
    }
  }

  export { Later}