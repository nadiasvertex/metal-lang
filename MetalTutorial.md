## 1 Introduction ##

> The metal language is designed to be a pragmatic composition of the functional, object-oriented, and message-passing paradigms. It does not attempt to be pure in any degree, except in it's adherence to the principle of least surprise and in making the right thing to do the easy thing to do.

> It bears many similarities to Objective C and Javascript. If you have a reasonable grasp on either of these two languages, metal will be trivial to learn. Some parts of metal were inspired by Haskell and Scala, but the implementation of those features bears little resemblance to their counterpart constructs in either of those languages.

> Without further ado, we begin.



## 2 Documenting Your Code ##

> Possibly the most annoying thing about writing code is documenting it. There are a lot of fine tools to help you with this onerous process, but many of them require adding additional redundant notation. Blech.

Python introduced docstrings, which are a fantastic idea. Unfortunately, the language did not take them far enough. Metal allows you to annotate just about anything with a docstring, including variable and value declarations, function declarations, function parameter declarations, structs, struct member declarations, protocols, properties, failcodes and states.

> An example of docstrings:

```
study_process(
 string_t re : "regular expression to process",
 uint32_t idx : "the index in the Re string we are considering", 
 string_t buf : "the output buffer for the processed NFA", 
 uint32_t nalt : "number alternate routes", 
 uint32_t natom : "number of atoms", 
 conversion_state_t ss : "state stack for processing atoms") returns(string_t converted)
 : """Does the work of converting an infix re to a postfix re for easier NFA generation. Insert . as explicit concatenation operator.""", internal
```

> Docstrings are only one type of annotation you can add to many elements. Other annotations tell the compiler useful things about the code that it wouldn't otherwise know. These annotations are often referred to as attributes, and are broken out in tables in the sections covering the various language constructs.

> What makes docstrings and annotations superior to comments in the code? Essentially, they are part of the syntax tree. The compiler pulls them out an inserts them into the AST as it parses the code. Once it has done that, the compiler can generate executable code and readable documentation at the same time. (You may also choose to have it do one or the other.)

> Having such complete knowledge of the code base allows the compiler to build extremely comprehensive documentation, even providing graphical diagrams of flow, dependencies, and state machine transitions. When debugging, the compiler can even generate graphs of the AST expressions themselves using the graphviz DOT tool.

> Please document your code. As a person whose day to day job involves reading code other people have written, I can personally attest to the importance of code documentation. You never know, the next person trying to figure out what your code does might be you.

## 3 Types ##

> metal has an extremely powerful type system, which includes benefits from both statically typed and so called “typeless” dynamically-typed systems. The language has several primitive types, and syntactic sugar for some common compound types.


| Type Name | Sizes   | Description |
|:----------|:--------|:------------|
| bool\_t    | 1 bit   | The true/false primitive. You can never depend on this being represented by anything larger than 1 bit, and the compiler reinforces this. The only values that can be assigned to a bool are true and false. By default, boolean values are initialized to false. |
| uint      | 8,16,32,64 bits | The uint primitive is an unsigned integer of various sizes. The full type name is constructed by appending the bit size and t to the name. So an 8-bit unsigned integer is uint8\_t. |
| sint      | 8,16,32,64 bits | The sint primitive is a signed integer of various sizes. The full type name is constructed by appending the bit size and t to the name. So an 8-bit signed integer is sint8\_t. |
| float     | 32,64 | The float primitive is a variable precision number of various sizes. The full type name is constructed by appending the bit size and _t to the name. So a 32-bit real number is float32\_t._|

On these primitives all other language features are constructed. Some built-in compound types are defined by the compiler, and have special language support.

| Type Name | Description |
|:----------|:------------|
| string\_t  | A mutable, variably sized list of primitives of the character type defined by the compiler. This can be changed at compile time, but not run time. By default it is uint8\_t. |
| type\_t    | A compound type which contains information about a type, including it's name, and various other pieces of information the RTE needs. It can be used for finding equivalent types. |
| any\_t     | A compound type used to bind storage of any type with information identifying that type at runtime. This is metal's dynamic type. |
| failure\_t | A type implicitly passed back from every function call, containing any failure information. On pass the failure is empty (null). When a failure occurs information regarding the failure is generated an assigned to the fail slot in the function's return parameter list. |

> The compiler defines some type aliases that are platform dependent. It is important to use these in some cases, but most of the time you should use the size that you intend. The big exceptions are when the type you intend varies by platform. One good example of this involves strings. How big is the character component of the string? Well, it depends. The compiler can be directed to make the char type anything from a uint8\_t to a uint64\_t. Type aliases allow you a safe, portable way of using the correct type. NOTE: Beware of linking modules compiled with different basic word and character settings. This can cause significant breakage.


| Type Name |  Description |
|:----------|:-------------|
| char\_t    | An alias for the integer type used as the base for strings. This defaults to uint8\_t, but can be overridden at compile time. |
| word\_t    | An alias for the native word size on the machine. For 32-bit architectures this defaults to uint32\_t, and for 64-bit uint64\_t. |

### 3.1 Arrays and Vectors ###

> metal supports fixed-length groups of the same type. These groups are allocated right next to each other in memory, and can neither grow nor shrink. They are fixed in length at their point of definition. While arrays and vectors are very similar to each other, they have important differences.

#### 3.1.1 Arrays ####

> These are the same sorts of structures you are familiar with from other languages.

```
var uint32_t[10] my_array; // an array of uint32_t's, 10 elements long.
var t := my_array[0]; // a dereference of the array using an index.
var t2 := my_array[12]; // compile-time error, index out of bounds.
```


> In the example above we declare an array of ten uint32\_t's. The buffer for this memory will end up being 40 bytes long, which gives us exactly enough space for 10 32-bit integers. We can retrieve the value of any index in O(1) constant time. Additionally, if we know the length of the array at compile time we can check that you are not indexing outside it's bounds.

> There are no restrictions of the length of an array, other than that it must fit into available memory.

> The compiler defines some operators on all arrays.


| Operator | Description |
|:---------|:------------|
| +        |  Appends the two arrays together. Returns a new array. |


#### 3.1.2 Vectors ####

> These structures are very similar to arrays, with the restriction that their length must be a power of two and their type must be an underlying primitive (ie. Integers, floats, no arrays or structs.) In addition, vectors are designed for parallel data operations, and are considered a first-class type.


```
val float32_t<4> colors1(1.0, 0.5, 1.0, 0.5); 
val float32_t<4> colors2(0.1, 0.1, 0.1, 0); 

val brighten = colors1 + colors2; 
val darken = colors1 – colors2;
val scale = colors1 * colors2;
```


> The example show us initializing two vectors, and then performing a variety of arithmetic operations on them. The compiler automatically uses SIMD operations when generating code for vectors.

### 3.2 Dynamic types ###

> The dynamic type holds a pointer to memory for the storage of the variable's value, bound with a pointer to the type information for that value. The advantage is that the any\_t type can hold a reference to any type. It is generic storage, which is extremely useful when you need it. The disadvantage, of course, is the memory overhead involved.

> Some argue that dynamic typing is dangerous, others that it is inefficient. To an extent, they are both correct. However, it should be recognized that when used in moderation dynamic typing makes a program simpler and clearer. While many sophisticated statically typed languages can allow you to emulate dynamic types, they do so at the cost of increased complexity and opacity. In addition, the programmer in need of such a solution either has to roll his own, or find and understand a library which does the requisite work. Even in such cases, the libraries are almost universally cumbersome. For example, compare writing C extensions for Python, versus actually writing code in Python.

```
val any_t a := “string”; // generic types
val any_t b := 100;
val any_t c := 3.14;

val d: = 50;	// NOT a generic type. 
```

> It is important not to confuse generic types with automatic typing. When you use val and var without a type, the compiler figures out what static type it should have, and then assigns that type to the variable (or value.) From then on the type is set in stone. Dynamically typed variables can change types whenever they want, though.

```
var any_t a := 10;

a $= 5.5;
a $= 10;
a $= “a string”;
a $= some_struct(1, 5);
```


> All of the assignments above are perfectly legal. Of course, you want to avoid using dynamic types to store numbers when possible, only because of the gigantic overhead involved—depending on the number size. However, it is comforting to know that the flexibility is there if you need it.

#### 3.2.1 Getting the type of an any\_t ####

It's all well and good to have a generic type, but if we don't know what type it is, how are we any better off than using C's “void **”? Therefore, metal provides a keyword “type” which provides a reference to a structure of type “type\_t”.**

```
var any_t a:= 10;
val a_type = type(a);
```


> We can see from this example, that getting the type is very simple. What can we do with it?

```
val any_t a:=”a string;
val type_a := type(a)
val is_str := type_a == type(string_t)
val type_name := type_a.name;
```


> metal provides extensive runtime information about types. If you would like to know more about the details of what is recorded and what is available at runtime, see the chapter on “Runtime Type Information”

#### 3.2.2 Dynamic type classes ####

> It is nice to have a generic type like any\_t, but in some situations it is overly permissive. For example, what if I wanted to restrict the value to being a certain set of structs? In that case you can use a type class restriction.

```
struct a { uint32_t v; };
struct b { float32_t v; }; 

val any_t<:a:> c := a(); // legal, compiles and runs.
val any_t<:a:> d := b(); // illegal, will not compile.

test(any_t v) returns()
{
 val any_t<:a:> e := v; 
}

test(b()); // illegal – compiles, but will fail at runtime. 
```

> This example introduces type classes. They are clearly visible as the “<:” followed by the identifier and then ":>". As this example also shows, type classes can be resolved at compile-time or run-time, at the compiler's pleasure. In general the compiler will try to catch violations at compile time, but in circumstances where that is not possible it will generate code to perform the check at run-time. We can see one of those circumstances where we are restricting an assignment from a function argument. Since the function argument itself has no type class restriction, it is hard, and sometimes impossible, for the compiler to know what kind of value is going to be passed in at compile time. The type class above is extremely simple. Normally you will not want to have a type class with just one type in it. (Otherwise, why not use the typename of the type you wanted in the first place?) Instead, you may want to restrict it to several kinds of structs.

```
struct a { uint32_t v; };
struct b { float32_t v; }; 
struct c { string_t v; }; 

val any_t<:a,b:> m := a(); // legal, compiles and runs
val any_t<:a,b:> m := b(); // legal, compiles and runs
val any_t<:a,b:> m := c(); // illegal, will not compile.
```


> The “,” operator means “or”. In fact, we can even use minimal wildcard syntax when constructing a type class.


```
var any_t<:%ary,postfix:> m := binary(); // matches

m $= unary(); // matches
m $= prefix(); // fails
```


> Here the “%” means “match any number of any characters.” It behaves much like the '%' operator in SQL, except that it is non-greedy. Type classes also support the '?' wildcard character.


```
var any_t<:?int8_t:> m;

m $= uint8_t(); // matches
m $= sint8_t(); // matches
m $= uint32_t(); // fails
```


> The '?' wildcard means any character in this position. As you might expect, using wildcard type classes at runtime is somewhat expensive in terms of performance, so again exercise prudence when using the extended facilities metal offers. In many situations the performance overhead will be offset by the increased flexibility and clarity of code, but overuse of this idiom can contribute to poorly performing applications.



## 4 Handling Errors ##

> Most languages provide some sort of error handling mechanism, and metal is no different. It too wants to be a cool kid. Personally, I think exceptions are almost a good method. The idea is nice, but the implementation is, IMHO, not (in any language, I might add.)

> Of course, one must expect errors. On the other hand, specifying what the error was, and why it happened is hard. The error handling mechanism in metal is integral to the operation of functions and messages. In fact, unlike exceptions, there is nothing exceptional about error propagation in metal.

### 4.1 Passing and Failing ###

> Every function and message in metal must pass or fail explicitly. The compiler won't even compile your program if you don't provide a pass/fail for every exit point in a function (with the exception of tail calls, which aren't, strictly speaking, exit points.)

> Passing is easy:

```
pass;
```


> That's it. The function will clean up, and return. The caller will be informed that everything went okay (unless you specified a function exit invariant contract that failed. More on that later.)

Failing is also easy, but requires slightly more thought.

```
fail <reason>;
fail_forward <reason>;
```

> Where “reason” is a failcode. Every failure must have a corresponding failcode. You cannot fail anonymously.

> The “fail\_forward” keyword means fail with this new code, but include the current failure information as a back-link in the failure data. This allows you to collect a chain of failures from the initial failure point all the way back up to an arbitrary point. It is much like a Java stack trace emitted when an exception occurs, except that certain functions in the call chain can be hidden, and a programmer may choose to truncate the failure information at any arbitrary point.

### 4.2 Failcodes ###

> Fail codes are 64-bit values created by generating a SHA1 hash of the module, subsystem, failcode name, and failcode description. As such there's no monotonically increasing values or fear of overlap. It is unlikely that two failcodes in the same program will ever overlap.

> You can specify failcodes like this:

```
failcodes <subsystem>
	<name> : <description> [, <name> : <description>, ...];

```

> An example of a failcode block:

```
failcodes Study
 unbalanced_parens : "The regular expression has unbalanced \
	parentheses and cannot be converted.",
 illegal_wildcards : "There are wildcard characters with nothing\
	to match.";
```


> In general, you never see the actual value of the failcode. It is used internally by the compiler to distinguish the reason for failing.

#### 4.2.1 Specifying a failcode during failure ####

> failcodes are internal to a module. One module may not specify a failcode from another module. The format for specifying a failcode is:

```
<subsystem>#<name>
```

> Or, for example:

```
fail Study#unbalanced_parens;
```


> This will cause the compiler to fill in a failure\_t structure with information on: (1) the failure code (2) the description from the failcode (3) the module name (4) the function name (5) the line number and column where the “fail” is located.

> In the future, I may expand this to be able to recover stack traces, but for now that's enough.


### 4.3 Retrieving information about a failure ###

> Every function has an implicit variable called “failure”, much like every C++ member function has a “this” pointer. When a function call or synchronous message send has failed, the failure variable will be a reference to a failure\_t containing the information above. Details about the failure\_t struct are broken out in the following table.

| Name      | Type         | Description    |
|:----------|:-------------|:---------------|
| code      | uint64\_t     | The failure code. This can be checked for equivalency using the “==” and “!=” operators. |
| description | string\_t | The description from the failure code's definition. |
| module\_name | string\_t | The name of the module the error happened in. |
| func\_name   | string\_t | The name of the function the error happened in. |
| line        | uint32\_t | The line number where the error happened. |
| col         | uint32\_t | The column of the character where the error happened. |
| prev        | self\_t   | A reference to the previous failure in the fail chain. This will be null if there are none. |


## 5 Storage Binding (Values and Variables) ##

> In metal you have two kinds of storage binding primitives: values and variables. A value is a once-for-all-time binding between a name and a storage area plus it's contents. It cannot be rewritten or rebound. A variable, on the other hand, can be rebound to different storage. Also, the contents of it's storage can change. In essence, values are very similar to runtime-evaluated constants, whereas variables are similar to what you find in most other procedural languages (like C and Javascript).

```
val a; // illegal, values must be initialized

val b := 10; // legal
b $= 15; // illegal, values cannot be rewritten

var c := 10; // legal
var d; // legal
c $= 15; // legal – variables can be redefined

var uint32_t e := 10; // legal, explicitly defined type
val f : “Holds some value” := 12.3; // legal, documented type
```

> The code snippet above introduces us to several other differences in metal syntax. Note first of all the usage of “:=” and “$=” instead of just “=”. The first operator is called the initialization operator while the second is called the mutate operator. It should be obvious then, that the initialization operator can only be used during initialization. Use of it in any other context is forbidden. The mutate operator is understood to change (or mutate) the left hand operand. In most cases this involves rebinding or changing the contents of the storage already bound depending on what kind of storage is represented. Note that there are additional variations of the mutate operator, such as “+=” and “-=”. These operators are qualified with additional names (such as the addition mutation operator) to distinguish them from “the” mutate operator.

> Note too that we didn't have to specify the type for the values and variables. Most of the time metal can figure out the type for you in these situations. When it can't it will provide you with an error message indicating it's failure, in which case you must specify the type.

> It is generally recommended to use values instead of variables wherever possible. With some thought, you will find that this is much easier than you might initially imagine. The named expression facility also aids in using values instead of variables.

### 5.1 Using Named Expressions ###

```
// Starting value
val exp_start : = exp from calc_fast_exp(x, (y-1)/2, N);

// Named expressions
step1 : (exp_start * exp_start) % N;
step2 : (step1 * x) % N;

// Calculation using named expression.
val exp := step2;
```

> In the code snippet above we are calculating an exponent. We perform the initial calculation by using a recursive function call. Instead of performing the next two steps in order and updating a variable, we express the operations to perform and then name them.

> The second step expands on the first step, and the final result is assigned to a value called exponent. At compile time the named expressions are expanded in place wherever they are used. Since the named expression uses only data loads, the compiler is free to more aggressively optimize it – including as much parallelism as possible.

> Additionally, named expressions allow you to break out the steps of a long or complex calculation -- making it easier to follow -- with no runtime penalty.

> Named expressions also allow you to do argument transformation, much like parameterized macros in C and other languages. Note that these are not quite as generic as C macros, but they do have the advantage of being part of the syntax understood by the compiler, and thus part of the AST. They are not bound by arbitrary whitespace rules.

```
/* Round 1. 
 Let [abcd k s i] denote the operation
 a = b + ((a + F(b,c,d) + X[k] + T[i]) <<< s). */

 F<x,y,z> : (((x) & (y)) | (~(x) & (z)))
 ROUND1_1<a, b, c, d, k, Ti> : a + F<b,c,d> + data[k] + Ti;
 ROUND1<a, b, c, d, k, s, Ti> :
	ROTATE_LEFT<ROUND1_1<a,b,c,d,k,Ti>,s> + b;
 
 /* Do the following 16 operations. */
 a $= ROUND1<a, b, c, d, 0, 7, T1>;
 d $= ROUND1<d, a, b, c, 1, 12, T2>;
 c $= ROUND1<c, d, a, b, 2, 17, T3>;
 b $= ROUND1<b, c, d, a, 3, 22, T4>;
 a $= ROUND1<a, b, c, d, 4, 7, T5>;
 d $= ROUND1<d, a, b, c, 5, 12, T6>;
 c $= ROUND1<c, d, a, b, 6, 17, T7>;
 b $= ROUND1<b, c, d, a, 7, 22, T8>;
 a $= ROUND1<a, b, c, d, 8, 7, T9>;
 d $= ROUND1<d, a, b, c, 9, 12, T10>;
 c $= ROUND1<c, d, a, b, 10, 17, T11>;
 b $= ROUND1<b, c, d, a, 11, 22, T12>;
 a $= ROUND1<a, b, c, d, 12, 7, T13>;
 d $= ROUND1<d, a, b, c, 13, 12, T14>;
 c $= ROUND1<c, d, a, b, 14, 17, T15>;
 b $= ROUND1<b, c, d, a, 15, 22, T16>;
```

> The above example is a snippet from the MD5 encoder that the metal runtime uses for hashing values. You can see that using parameterized named expressions is just like using functions, with the exception that the expression always has an output, and is always inlined directly into the source code.

> There are no special rules. You may consider parameterized named expressions to be like code templates. They are not “called” like functions, just like #define macros in C are not “called.” The arguments are replaced and expanded inline during the constraint checking pass.


### 5.2 Module-level variable definition and access ###

> You might be wondering at this point, “what is a module?” A later section will cover this fully, but for the moment it is good to understand that a module is an implicit organization of functions, protocols, structs, values, and variables, generally encompassing all of the contents of a single file. The name of the module is the same as the name of the file without the extension. Modules provide a name space much like namespaces in C++ and modules in Python.

> There is no such thing as a C-style global variable in metal, only module-level variables. Modules implicitly define and limit scope. Within that scope you can allocate certain storage with the guarantee that it will exist if the module is imported. On the other hand, that very guarantee implies certain restrictions with respect to the initialization and construction of that storage. The following subsections provide details regarding storage defined at module-level scope.
5.2.1Module-level Constants

> In addition to read-only storage that can be initialized at runtime, metal also supports read-only storage initialized at compile time. These are called constants, as you would expect. They are simple constructions with module scope, using the “val” keyword.

```
// A compile-time constant integer
val my_constant := 10;
// Constant string
val some_name := “it's value”;
Constant 64-bit 
val uint64_t := 1;
```

> From the example above, you can see that declaring module-level constants is very similar to their counterparts in functions. The only difference is that a module level constant must be fully resolvable at compile-time, while function-level val statements may be resolved at runtime.

#### 5.2.2 Module-level Variables (“Global” variables) ####

> In the same way as you can create module-level constants, you can create module-level variables. These variables are also initialized at compile-time (if they are initialized at all), but they can be changed.

```
var a:=1; // Variable with module-level scope.

my_func() returns ()
{
 var b:=2; // Variable with function-level scope.
 var c:=a; // Variable with function-level scope accessing a
	// variable with module-level scope.
 a $= b; // Also legal.
}
```


> Something important to understand is that module-level variables and values are not global in the sense that any code in any module can automatically access them. If another module wishes to have access to a variable or value defined at module scope they must import the module and use the proper scope name to access it.

#### 5.2.3 Module scope access ####

Variable name resolution uses typical most-closely-nested rules. Notice the following example:


```
// module_1
var a:= 10;
```

And the next module:

```
// module_2
import module_1;

var a:= 50;

my_func() returns ()
{
	val test1 := a;
	val test2 := module_1.a;
}
```


> The two modules both define a module-level variable of the same name. The two variables do not conflict when module\_1 is imported into module\_2 because they both have their own name space.

> The code in module\_2 does have access to module\_1's definition of 'a' through the import statement, though, and you can see how it is accessed in the initialization of 'test2'.

### 5.3 Automatic Garbage Collection ###

> As mentioned earlier, all compound types are created on the heap. Always. Partly this is to simplify tail-call semantics, but it also helps to simplify the automatic garbage collection facility.

All compound types have reference counters embedded into them. Whenever a variable is bound to a data structure, that variable will follow this algorithm:

  1. Increment the reference counter on the object to be assigned (if it is not null.)
  1. Is the current reference non-null? If so, decrement the reference counter, otherwise go to step 4.
  1. Is the reference counter zero? If so, call the destructor for this type. (Destructors are automatically generated by the compiler and are not programmer-accessible.)
  1. Bind this variable name to the object.

> This simple algorithm is reasonably deterministic. Everything will be freed as soon as all references to it are gone. If you have a large root object that suddenly becomes available for harvesting, you may find the current thread pausing momentarily to process the destruction chain. In order to alleviate that, I may provide a facility to allow incremental garbage collection.

> You cannot “force” something to be destroyed. The reference chain is one-way only. An object does not know who may have references to it, so it cannot update them. The best way to make sure you are not hanging onto an object is to assign the variable the “null” value.


## 6 Functions ##

> Not being a pure object oriented language, metal allows functions at the module level. These are not quite like global functions in C. Instead, they resemble most closely module-level functions in Python. Unlike Python or C++ however, functions are not allowed in protocol objects. Instead, function-like constructs called messages are used.

### 6.1 Functions vs. Messages ###

> A function in metal is much like a function in C. It has link-time binding and is executed with a direct call (and in some cases perhaps an indirect call.) In addition to those features, functions in metal are first class objects and may be passed as parameters. Functions can be part of lambda expressions and support tail calls. They also support multiple named parameter return.

> Messages are very similar, but have the following differences: Most importantly, messages are runtime-bound. While this makes them far more flexible, it also makes them far slower. Secondly, messages always include an object pointer called self. This is much like the “self” variable in Python, except that it is implicit (like this in C++). Finally, not only can messages fail to execute properly, they can fail to “send”. That is, if you send a message to a protocol object that does not support that message, the send will fail.

> Consider the following example:

```
protocol myProtocol
{
 add(uint32_t x, uint32_t y) returns (uint32_t result)
 {
 result := x+y;
 pass;
 }
}

test(myProtocol p) returns ()
{
	val r1 := result from 
	add(10,15) -> p; // legal, compiles, sends

	val r2 := result from
	sub(100,80) -> p; // legal, compiles, FAILS SILENTLY!
}
```


> While the program compiles and runs, it does not run correctly. That is, while you are expecting that [r2](https://code.google.com/p/metal-lang/source/detail?r=2) will have a value of 20, it in fact will have a value of 0. That is called a send failure, and is by default silent. Note that, while that seems very dangerous, there is a good reason for it, and a very easy way to either check for the failure, or to ensure that the protocol of the object in question is the same as the version you are expecting.

```
test(myProtocol p) returns ()
	require:
	p has_aspect myProtocol; // function fails to execute
	// if p doesn't have 
	// myProtocol support in it
{
	val r1 := result from 
	add(10,15) -> p; // legal, compiles, sends

	val r2 := result from
	sub(100,80) -> p : fail of msg#send -> sub_send_failed,
	otherwise -> fail_forward;
	// legal, compiles, 
	// fails with notifications.
}
```

> As a quick and simple example, note the code above. It implements two forms of error checking.

> The first is a built-in function that ensures that protocol reference “p” supports all of the messages indicated by the protocol named “myProtocol.” This check is executed at runtime. So long as you know that all the messages you are sending are part of the protocol, that check is enough to keep send failures from happening in that function or message body.

> The second is the fail pattern matching predicate. This feature allows you to map various failure codes to state-machine states (see chapter FIXME on State Machines.) If a failure occurs, the corresponding state is activated, allowing you to deal with the situation. In this case, if there is a send failure that may be handled locally. Otherwise the failure is forwarded to the next nearest nesting level. (That is, the function returns, or message completes it's send, but both indicate an execution failure and forward the failure information to their caller or dispatcher.)
6.2 Defining a Function

It is very easy to define a function. This part is very similar to just about every language you may have ever used. The function is named, inbound parameters are specified, outbound parameters are specified, and any function attributes are specified. Functions can also include docstrings (like most other definable objects in metal.)

```
myfunc(sint32_t a, uint32_t b) returns(uint64_t c, uint64_t d)
 : “Perform some operation.”
{
 // body
}
```

The returns clause in the function definition must exist, even if the function does not return anything. Functions do not need to be declared, just defined. (ie. There are no function prototypes like C and C++ have.) Also, functions do not have any ordering problems. You may call a function that is defined after the function that it is called from. You may call functions in other modules using the scope resolution operator.

```
import othermodule

myfunc(sint32_t a, uint32_t b) returns(uint64_t c, uint64_t d)
 : “Perform some operation.”
{
 val tmp := result from othermodule.otherfunc(a,b);
}
```

### 6.3 Keyword Arguments ###

**Revise this section.  I dislike intrinsics now.  They are inelegant and create de-facto syntax that, although not part of the language, essentially becomes part of it.  Instead, add an attribute to a parameter called kwarg.  That parameter must implement the dictionary protocol.  The compiler will generate automatic calls to the dictioanry object to add the keyword arguments and their values.**

A function may be passed keyword arguments, just like Python. These are arguments that are in addition to the positional ones, not instead of. Keyword arguments can be used to provide a certain flexibility in processing, without require dangerous untyped mechanisms. Granted, there is a small performance hit, but it is well worth it. Functions with varargs requirements shouldn't be in the critical path in any case.

```
log(string_t info) returns()
 : “Perform some operation.”
{
 val uint32_t log_level := `get_kwarg(“loglevel”, 0);
 val bool_t break_newlines := `get_kwarg(“breaknewlines”, false);
 
 // ... log the data 
} 
```

> As you can see, there is no change to the signature of the function. Any keyword arguments are passed implicitly with the rest of the function parameters.

> What are the strange looking calls with the back tick before them? Those are intrinsics. Metal supports a large variety of intrinsics that are not part of the language proper, but are a sort of built-in library. Mostly these are things that you could do in the language anyway, but it would be inconvenient to do by hand. In the case of keyword arguments, you could use the implicit variable “args” to retrieve the map containing the arguments, and then call the RTE function “rte\_get\_kwarg\_ref()” to get a reference to the struct containing the type and value information for that argument. If that function fails you could assign a default value, otherwise you would still have to retrieve the value, and cast it to the appropriate type (using more intrinsics.)

> In this case, the intrinsic saves you a lot of typing, and is less error prone. In other cases intrinsics do things that you cannot easily do any other way. For more information on intrinsics, see section FIXME.

> The intrinsic “`get\_kwarg” takes a string identifying the name of the keyword argument, and a default value in case the argument is not present. Note too that the value (or variable) must be explicitly typed. The compiler can't know at compile time what type is going to come out of the dictionary, so instead you must tell it. If the argument type is not castable to the value or variable type, the intrinsic behaves as if it were not present and instead assigns the default value.

> In essence, this means that the keyword argument must match the type AND the name in order to be found.
6.4 Invariant Testing (Or Contract Violation)

> In order to facilitate robust code, metal provides built-in invariant testing in the form of the require and ensure keywords, proudly stolen from the eiffel language. These cause the function to require certain conditions prior to function execution, and to ensure certain conditions afterwards. If any of these conditions are violated the function execution fails, and failure information is set that describes the failure.

> You can think of require and ensure as clauses in a contract between the function and it's callers. The require clause is a guarantee between the callers and the function that they won't pass in invalid data. If they do, the function will not execute. It is the caller's responsibility to make sure that it is passing valid information in.

> On the other hand, the ensure clause is a guarantee between the function and its callers that it won't hand them garbage. If there is a failure, the obligation of the function is to notify its callers that the results cannot be trusted.

```
myfunc(sint32_t a, uint32_t b) returns(uint64_t c, uint64_t d)
 : “Perform some operation.”
 require:
	a < 100 : “a is too large”,
	a > -100 : “a is too small”,
	b != 0 : “b must not be zero”;
 ensure:
	c!=d : “c and d were identical and should not be.”;
{
 // causes the function to fail because of the ensure clause
 d := 5;
 c := d if a == 0 else b;
}

test() returns ()
{
	myfunc(1000, 100); // fails because the require clause
	myfunc(0,1); // passes the require, but the function will
	// still fail because the ensure clause will
	// catch the post-execution contract violation
}
```


### 6.5 Attributes ###

> Functions can also have attributes specified. Do not confuse these with protocol properties, they are very different. Attributes indicate certain flags that apply to the function. Common ones include “deprecated” and “obsolete”. Attributes indicate to the compiler special information that it can use when generating code, or checking for errors.

| Attribute     | Applies To  | Description  |
|:--------------|:------------|:-------------|
| deprecated    | func/msg    | The function or message is deprecated. Calls to the function, or sends of the message will cause a warning diagnostic to be emitted by the compiler. |
| obsolete      | func/msg    | The function or message is obsolete. Calls to the function or sends of the message will cause an error diagnostic to be emitted by the compiler. Code will still be generated for it though, as you may be trying to maintain binary compatibility with older clients. |
| no-gc         | func        | Tells the compiler that garbage collection information must not be emitted in this function. No automatic garbage collection will take place. Note that you should really know what you are doing if you specify this attribute. |
| no-rte        | func        | Tells the compiler that it must not make calls to the RTE in this function. If this is specified, any language feature which requires the RTE will cause an error diagnostic to be emitted by the compiler. |
| internal      | func/msg    | Tells the compiler that this function cannot be called by external modules. This means that the compiler can optimize the function more heavily, and it will also be hidden from the link process. Similar in nature to C's “static” function qualifier. |

### 6.6 Guarded Functions ###

> Another feature of functions in metal involves guarded functions. While this may sound like a lot like invariants, that is not really the case.

> Guards separate one large function body into several smaller bodies. The first of those bodies who's guard allows it to pass is executed as the function body.

```
test_guards(uint32_t value) returns ()
	guarded
	when value == 1
	{
	con_write_str("guard is 1");
	test_guards(0);	
	}
	
	otherwise
	{
	con_write_str("guard is not 1");
	pass;
	}
```

> As you can see from the example, you must specify that a function is guarded. After that specification are a series of when clauses followed by the body to be execute when that clause is true. Finally, there may be an otherwise clause executed when no other clause matches.

> It is important to remember that only one clause is executed on any entry into the function. When combined with efficient recursion, guarded functions can generally be substituted for all procedural loop and if/then constructions. In fact, metal does not provide any “for” or “while” style looping. I know that may feel strange, so we will now consider how to accomplish looping in metal.


### 6.7 For-style Loops ###

> The basic pattern of a for-style loop is execution in series. Loop through a series of values until the exit condition becomes true.

```
for_loop(uint32_t index, uint32_t bound, uint32_t[] collection) 
	returns ()
	guarded
	when index < bound
	{
	do_something(collection[index]);
	for_loop(index+1, bound, collection);
	}
	
	otherwise
	{	
	pass;
	}

```

> The function is called with the initial index, the boundary condition, and perhaps some collection to iterate through. The guard is used to make sure that the boundary is honored. Once the boundary is reached, the function terminates.

> Since metal supports efficient recursion, the recursive call is converted to a tail call, reducing both the execution time and the memory space needed. In fact, in many cases the optimizer may convert the tail call into a for-style loop on the back end.

> This kind of looping function can be generalized greatly using lambda expressions. We shall do so later, when we talk about lambda expressions in more detail.



### 6.8 While-style Loops ###

This pattern is to execute a body of code until the given condition is true. One can see quite clearly how this generalizes from the for\_loop.

```
while_loop(uint32_t cond) returns ()
	guarded
	when cond == true
	{
	cond := result from do_something();
	while_loop(cond);
	}
	
	otherwise
	{	
	pass;
	}

```

> The body of this function is executed continuously so long as the condition remains true. Again, we can see that while this would normally take up an incredible amount of stack space, using tail calls allows us to execute it in the same memory space as an iterative while-loop would require.

> It can also be generalized using lambda expressions, which we'll consider later.


## 7 Messages and Protocols ##


> We covered some aspects of messages in the section on functions, in order to illustrate some of the differences between them. As a brief recap, use functions when low-level execution or speed is imperative. Use messages the rest of the time.

> A protocol is a set of messages accepted, as well as data bound to a name. That name is used to identify the protocol. A protocol is very similar to a class in most languages, with the exception that the data bound to a protocol is not available outside the protocol. To explain that fully, an example is in order.

### 7.1 Properties ###

```
protocol A
{
	properties:
	uint32_t length,
	string_t name;

	set_length(uint32_t l) returns ()
	{
	mutate self
	{
	length $= l;
	}	
	}

	get_length() returns(uint32_t length)
	{
	length := self.length;
	}
}

test() returns ()
{
	var a_inst := construct() -> A;

	val length1 := a_inst.length; // illegal, will not compile.
	val length2 := length from get_length() -> a_inst; // legal,
	// compiles	
}
```

> From this example we can see that reaching into an object and pulling out data is not allowed. You must request the data by sending a message to the object. “This is so slow!” you might complain. That is true. It is designed to be so. Protocol objects are designed to be black boxes for purposes of data processing, not smarter structs. In fact, a protocol object might not even be in the same process or the same machine as the code sending the message, and we don't want to pretend otherwise. If you want to group data and have fast access to it, use structs. That is what they were designed for.

> Inside of a protocol object, property access is very fast. There is nothing special about the attributes themselves. They can be any valid data type supported by the language. They have no “protection” mechanisms ala C++ or Java because access to them externally is forbidden and metal has no concept of inheritance.
7.2 Messages

> Defining a message is very much like defining a function, except that it must be done inside of a protocol definition. Also, the parameters and environment of a message are called it's payload, because it varies somewhat from a function on the ABI level.

> We have done this several times already, as you may have noticed.

```
protocol A
{
	send_me() returns ()
	{
	pass;
	}
}	
```

> Nothing earth-shattering here. Message definitions are identical to function definitions, with the one exception that not all attributes which apply to functions can apply to messages, and vice-versa. The table under the function attributes section above contains more details about which attributes may be applied to each kind.

### 7.3 Forwarding Messages ###

One of the interesting applications is the ability to forward a message to a different destination. For example, consider a simple application: tracing. You would like to be able to trace the activity of certain objects, without having to instrument each message, or clutter up the protocol with extraneous mixins.

What you would really like to be able to do is to somehow wrap your object in another object, which would would log all messages and perhaps their payloads, then transparently forward the message to the original destination. This sort of application appears below.

```
protocol Trace
{
	properties:
	any_t tracee; 

	construct(any_t tracee) returns ()
	{
	mutate self
	{
	tracee $= tracee;
	}
	}
	
	log(@string_t info) returns ()
	{
	// do some logging.
	}

	__dispatch_unknown_msg__(@string_t msg_name, msg_id_t msg_id,
	@payload_t payload)
	returns ()	
	{
	log(msg_name);
	`forward_msg(msg_id, payload, self.tracee);	
	}
}

test() returns ()
{
	var my_obj := construct() -> SomeProtocolObject;
	var tracer := construct(my_obj) -> Trace;

	some_msg() -> my_obj; // Goes straight to my_obj.
	some_msg() -> tracer;	// Goes to my_obj via tracer.
}
```


All protocols have a special message called “dispatch\_unknown\_msg” which is called when the RTE dispatcher cannot find a message handler for a message sent to the object. If that handler exists, then the dispatcher forwards the message to that message handler. User code can do anything they like to the payload (which contains the inbound and outbound arguments, any keyword arguments, as well as failure information.

Using the “`forward\_msg” intrinsic, the payload can be transparently redirected to some other object. Message forwarding provides a foundation on which many other behaviors can be built. For example, run-time polymorphism.

### 7.4 Runtime Polymorphism and Overloading ###

> Imagine that you want to write a function that adds two integers together. This is trivial. Later, you decide that you need a function that also adds two floats together. Suddenly you have a problem. The metal language does not support function overloading, so you have to have two functions, presumably named add\_int and add\_float. In addition, you always need to know which of those functions to use. While that may not be a big deal for this small example, you can likely imagine that this sort of behavior gets out of hand when you have a large number of potential candidates.

> While it is true that metal does not support function overloading, it does support message overloading. A message is identified by a 64-bit ID .


**This section is not complete.**

## 8 Structs ##

> Structs are user defined types. They are no different from structs in C, with some extensions. Structs can be self referential, and can contain members of any type. They cannot be self-nesting, as you can imagine.

> In addition to providing variable grouping, structs provide built-in reference counting and locking semantics. The additional information to support those semantics is tagged onto the end of the memory allocated for these structures. This is useful for saving them to disk or transmitting them over some sort of communications system.

```
struct my_data_type
{
 uint32_t a;
 uint32_t b;
 float c;
 string_t d;
};
```

### 8.1 Creating instances of structs ###

There are two ways of creating a struct: dynamic allocation and static allocation. When using dynamic allocation a struct is always created on the heap. They cannot be created on the heap. The lifetime of a struct depends entirely on references to it. Once all references to the struct are gone, the struct is immediately freed.

The second way to create a struct is using static allocation. The memory is allocated at compile time. If there are initializers, they must be constant values that are resolvable at compile time. The lifetime of the struct is the lifetime of the program.

```
struct sa
{
	uint32_t[100] a;	
};

struct sb1
{
	uint32_t b;
	sa c; // The entire struct sa is nested in this struct.	
};

struct sb2
{
	uint32_t b;
	@sa c; // A reference to struct sa is generated, and which 
	// is initially null
};	

struct sb3
{
	uint32_t b;
	uint32_t[100] a; // This is essentially the same as sb1, except // without the hierarchical access.
}
```

> Variables which refer to structs are always references, except in the following simple case: When defining a struct which has an embedded struct, by default the data type is simply embedded directly into the struct. You must deliberately indicate that you want a reference in this case. Consider the following example:


> When we defined sb1 we did not specify a reference. Therefore, it is as if we defined sb1 the way we defined sb3. The entire contents of sa are embedded in sb1. The size of sb1 is therefore probably 404 bytes, just like sb3.

> On the other hand, sb2 has a reference to sa. It's entire size is more likely 8 bytes. Unless initialized differently, the “c” member will have a null value.

#### 8.1.1 Initializing Structs ####

> Structs can be initialized using constructor syntax. While they do not have (or support) actual constructor functions, the compiler synthesizes the construction as if it did. Additionally, initialized structs can have two sorts of classes: mutable and immutable.

```
struct my_data_type
{
	uint32_t a;
	uint32_t b;
	float c;
	string_t d;
};

// Static initialization – mutable struct
var g_test1 := my_data_type(1, 21, 8.9, “some string value”);

// Static initialization – immutable struct
val g_test2 := my_data_type(9, 75, 9.5, “some string value”);


myfunc() returns ()
{
	// Dynamic initialization – mutable struct
	var test1 := my_data_type(5, 10, 3.2, “a string value”);

	// Dynamic initialization – immutable struct
	val test2 := my_data_type(7, 11, 3.9, “a string value”);
}
```

> As the example above shows, struct creation and initialization at the global scope is done the same way in both situations. In the first two initializations the space for the data is set aside at compile time, and the initialization is also done at compile time. Therefore, the initialization imposes no overhead.

> In the second two initializations the storage is allocated at runtime, and the initialization is also performed at runtime. A certain amount of overhead is involved, but some of that is unavoidable. In order to minimize the dynamic allocation overhead metal can generate optimized allocators for each struct type. The trade-off is slightly increased memory usage for, in some circumstances, vastly increased speed.

### 8.2 Case structs ###

> Imagine a situation where you have several related structures that should get initialized, depending on the value of the initializer. For example, let's use the example of an expression evaluator for a very simple calculator.

```
struct num_t
{
	uint32_t value;
};

struct binary_op_t
{
	string_t op;
	@num_t left;
	@num_t right;
};
```

> There is a fundamental flaw in these structs. You can't have trees deeper than 1. For example, 2 + 3 is representable, but not 2+3+4.

```
val a := binary_op_t(“+”, num_t(2), num_t(3)); // legal, compiles
val b := binary_op_t(“+”, a, num_t(4)); // illegal, type mismatch 
```

> In order to correct this, we have to introduce dynamic types.

```
struct binary_op_t
{
	any_t left;
	any_t right;
};
```

> This resolves the first problem, that of legality. We can now make deeper trees with no problem, but we still have to remember to use the right struct initializers. Granted, for our very small example here, that's not a big deal. For larger projects it becomes a tedious annoyance, and perhaps even a maintenance problem.

> The answer to this sort of problem is pattern matching in struct creation. metal allows you to specify data patterns that it will later match up. The compiler writes out all of the different types, instead of forcing you to do it by hand. In addition, when you instantiate a node using case structs, the compiler transparently creates an instance of the correct concrete type for the pattern.

```
struct expr_t
 match case num_t(uint32_t value);
	case binary_op_t(string_t op, 
	any_t left, any_t right); 
```

> The names of the matching cases need to be unique to the local module, other than that there are no surprising rules. They are in all other ways the same as “normal” structs. The only real difference is that the compiler generates some helper code to assist in initialization.

```
val a := expr_t(10);	// becomes num_t
val b := expr_t('+', 2, 3); // becomes binary_op_t
val c := expr_t('*', a, b); // also becomes binary_op_t
```

> How do you access the values? The same way that you would any normal struct.

```
val a:=expr_t(10);
val b:=a.value;
```

> The compiler generates structs with members named after the parameters of the case structs, and in the same order as they are in the pattern. What if you don't want the binary\_op\_t to match any type, but you do want it to match a certain range of types?

#### 8.2.1 Type class restriction in case structs ####

> In our example of the expression tree above, we have decided that we want to include variables, and differentiate between constant binary nodes and variable ones. In that case, we can use type restriction.

```
struct expr_t
 match case num_t(uint32_t value);
	case var_t(string_t name);
	case const_binary_op_t(string_t op, 
	any_t<:num_t,const_%:> left, 
	any_t<:num_t,const_%:> right); 
	case binary_op_t(string_t op, 
	any_t left, any_t right); 
```

> The '<:' and ':>' brackets after any\_t indicate a type class, which was discussed in section 3.1.2. In the pattern matching sequence, we see that we have use the type class specifier we learned about in an earlier section to restrict matching. As in all cases of type classes, matching is done as much at compile time as possible, in order to increase runtime performance.

### 8.3 Struct attributes ###

When defining a struct you may specify certain attributes that control how the compiler generates and uses the underlying representation. A table of values follows.

| Attribute         | Description    |
|:------------------|:---------------|
| packed            | The compiler will not pad the structure's data members to optimize alignment for various processors. |
| no\_cache          | The compiler will not emit an optimized memory allocator for this struct. All allocations of this data structure will go directly to the main allocation function. When this is not specified, the compiler will emit code that constructs a cache specifically for this data structure. Allocations and deallocations will be amortized O(1). |
| docstrings        | The docstring is an actual string, and it must be the first item in the list. The docstring is used when generating documentation, and can be looked up at runtime for informational purposes. |


> An example of using struct attributes:

```
struct a_disk_header_struct 
	: “Information about the file layout”, packed, no_cache
{	
	uint8_t tag;
	uint32_t data; 
};
```

> There is a good chance that the compiler would pad the data structure shown above, in order to optimize access to the “data” member. However, since this is a structure that we are going to write to disk, we don't want the extra space there. Also, other architectures might pad this structure differently, so if we read it back somewhere else there is a good chance that the data would be garbled.

> Additionally, since this is a header to the file, we know that we are going to allocate very few of these. Therefore, it makes good sense to tell the compiler not to bother optimizing allocation of this struct.

### 8.4 Operators ###

> Many languages have the ability to perform operator overrides for user-defined types, metal is among them. Operators only work with structs, which are what metal considers it's user defined types. Protocols are a completely different sort of abstraction.

> Different operators have different signatures and semantics. You must understand the semantics of the operator in order to use it properly. For example, consider the addition operator:

```
struct ex1
{
	uint32_t a;
	uint32_t b;
};

operator “+” ex1(ex1 left, ex1 right) returns (ex1 result)
{
	result := ex1(left.a + right.a, left.b + right.b);
	pass;
}

operator “+” ex1(ex1 left, uint32_t right) returns (ex1 result)
{
	result := ex1(left.a, left.b + right);
	pass;
}
```


> This operator is extremely simple. It takes two arguments: a left and right value, and returns a single result. If the operation succeeds then we pass, otherwise we may fail. We can also use guards and contraints in an operator, just like with functions.

> An important thing to realize is that operators are just functions with a special syntax, and special constraints. The signature of an operator must match a certain pattern. For example, the addition operator above must take a reference to an “ex1” struct as the first parameter, and must return a reference to an “ex1” struct. The second parameter may vary.

> Each operator has it's own rules for the signature acceptable to it. During constraint checking the compiler will make sure that the operator functions have the appropriate signatures. If they do not, an error diagnostic will be emitted.


| Operator             | Signature                 | Description |
|:---------------------|:--------------------------|:------------|
|+,-,**,/,%,&,|,^,>>,<<**| type(type, any\_type) returns (type) | Simple binary operators. |
| <,>,==,!=            | type(type, type) returns (bool\_t)   | Binary comparison operators. |
| [.md](.md)                   | type(type,any\_type) returns (any\_type) | Index operator |
| +=,-=,**=,/=,|=,&=,^=,<<=,>>=**| type(type,any\_type) returns () |  Self-adjust operators. |
| convert | type(type) return (conversion\_type) |


**This section is not complete.**

## 9 State Machines ##

> metal has built-in support for comapct state machine simulation. Quite a few programming exercises boil down to state machines. In many languages these are simulated using switch statements, in others if.. then, and in still others arrays or dictionaries with function pointers can be used. One problem of all of these methods is clear separation of states, as well as clear indications of dispatch.

> Having a simple language feature to support state dispatch makes efficient state machines easier to create, and it makes their operation more transparent to later readers of the code (even when the author is the later reader.)

> The following is a snippet of code showing part of a state machine for converting postfix-style regular expressions to their NFA representation. The “...” sections represent code that was omitted so that we can focus on the important parts.

```
convert_to_nfa( ... ) returns ( ... )
 guarded 
 when ...	
 {

 val c := postfix_re[idx];
 
 case c of
 $. -> concatenate,
 $| -> alternate,
 $? -> zero_or_one,
 $* -> zero_or_more,
 $+ -> one_or_more,
 otherwise -> normal_match;
 
 on normal_match
 {
 // Create a new state.
 val s := state_t(c, null, null, 0);
 // Create a new top for the stack.
 val top := frag_stack_t(fs, frag_t(s, null));
 // Next character please.
 convert_to_nfa(postfix_re, idx+1, top); 
 }
 
 on concatenate
 {
 // Get first to elements off of stack
 val e2 := fs.f;
 val e1 := fs.next.f;
 
 // Patch in the start states.
 patch(e1.out_list, e2.start);
 
 // Construct a new top element and link it to the stack.
 val top := frag_stack_t(fs.next.next, 
	frag_t(e1.start, e2.out_list));
 
 // Consider the next character.
 convert_to_nfa(postfix_re, idx+1, top);
 }

	...
 }

```

The state machine assist is composed of two parts: (1) state machines states and (2) state transitions (dispatching).

### 9.1 States ###

> All states for a given state machine must be inside the same function. This design is deliberate, and part of it's intention is to cause you to think about the state machines you are making. A large state machine likely has several subordinate state machines that are semi-independent of the whole. Breaking these up into various functions will make the operation of the state machine as a whole much more readable.

> An example of a state from the snippet above is:

```
on normal_match
 {
 // Create a new state.
 val s := state_t(c, null, null, 0);
 // Create a new top for the stack.
 val top := frag_stack_t(fs, frag_t(s, null));
 // Next character please.
 convert_to_nfa(postfix_re, idx+1, top); 
 }
```

> Each state is preceded by the “on” keyword. Following that is an identifier which must be unique inside the function, and follows the same identifier rules as variables and function names. A state is a sub-block of the function and has access to all of the values and variables defined in the function proper. Values and variables defined in the body of the state are destroyed on transition out of the state.

> State blocks also follow the same rules as function blocks. That is, the last line in a state block must be one of “pass”, “fail”, “transition”, or a tail call to the function itself. When a transition is made from the main body of the function to a state, you can never “return” to the main body of the function. State transitions operate exactly like a “goto” statement.

> If no state transition is made from the main body of the function, all the code in the various states is simply ignored, as if it did not exist. It is not possible to “fall” into or out of a state. All state transitions are deliberate.

For example, consider the following code:

```
...

val a:=1;

on some_state
{
	val c:=3;
	pass;
}

val b:=2;

...
```

There is no deliberate transition into “some\_state”, therefore the code is completely ignored. It is as if it looked like this:

```
...

val a:=1;

val b:=2;

...
```

In fact, if no state (including the base state of the main function body) transitions into a state, the compiler will issue a warning and will not even bother generating code for that state. (Although it is still error checked.)

There is no such thing as automatic state “memorization.” The machine does not remember what state it was last in. Every time you enter a function, the base state is entered. You must make a deliberate transition into a state.

It is up to the author to provide an efficient representation of state for any given state machine. The dispatch functions will transition the machine into the appropriate state by decoding your state representation for you.

### 9.2 State transitions (Dispatch) ###

There are two ways to transition between states: (1) direct transition, (2) pattern matching.


#### 9.2.1 Direct state transition ####

This is probably the least used transition mechanism, and is useful for going directly from one state to another. The syntax of the command is:

```
transition <state_name>
```

For example:

```
on state1
{
 transition state2;
}

on state2
{
 transition state1;
}
```

> The above example is basically an infinite loop. It operates precisely like a goto in procedural languages.

#### 9.2.2 Pattern matching state transitions ####

> The more common method is pattern matching, as it allows for simple conditional transition grouping.

> The basic syntax is:

```
case <expression> of
	<pattern1> [when <guard>] -> <state> || fail <reason>,
	<pattern2> [when <guard> -> <state> || fail <reason>
	[[when <guard> -> <state> || fail <reason>]
	[otherwise -> <state> || || fail <reason>]],
	...
	<patternN> ...
	otherwise -> <state> || fail <reason>;	
```

> Each pattern is a potential result of the expression evaluated at the top of the “case” statement. The pattern has the following syntax:

```
<value1> [|| <value2> || ... || <valueN> ] 
```

> You may match one of several different values with the pattern. In addition, a pattern can have one or more guard expressions.

```
<pattern> when <condition1> -> <state>
	when <condition2> -> <state>
	otherwise -> <state>
```

> For example, consider the following complex pattern in the RE to postfix RE matcher in metal's RTE.

```
case c of 
 $( -> open_paren, 
 $| -> alternate, 
 $) when natom>0 && ss!=null -> close_paren 
 otherwise -> fail Study#unbalanced_parens, 
 
 $* || $+ || $? when natom>0 -> wildcard 
 otherwise -> fail Study#illegal_wildcards, 
 
 otherwise -> normal_match;
```


> The third pattern matches only the close parentheses character “)”. However, it has two possible transitions. If the guard passes then it will transition to the close\_paren state, otherwise it will fail with an appropriate failcode.

> On the other hand, the fourth pattern matches three different possible inputs and also has a guard to make sure that there isn't some sort of error in the input. In this way we can efficiently and securely transition to states, happy in the knowledge that all our bases are covered, and not having to pollute our states with guard logic that doesn't belong in them.

> That last is important because the preconditions necessary to transition into a given state can be different from two different start states. If we were to put the guard logic in the states themselves, each state would have to know about all the states that can transition into them.     That breaks encapsulation, and is simply a bad idea.

## 10 Explicit Parallelism ##

> Breaking pieces of work up into bits that can run at the same time is the heart of parallelization. It is not really the compiler's job to figure out which bits can run at the same time, and which cannot. Instead, the language provides two different methods for specifying parallelism. One is for discrete operations, the other for much larger operations.

### 10.1 First Class Vectors ###

> metal supports first class vectors, in the same way that many languages support first class arrays. Vectors must be powers of two, and generally should be composed of primitive types for best effect.

When metal sees an operation occur on two vectors, (such as addition), it converts the operation into the most efficient SIMD instruction (or set of instructions) available on the platform. This sort of parallelism can be very efficient for certain kinds of workloads.

### 10.2 Work Queues ###

> The other, more generic feature of the language involves work queues. These are essentially just like thread pools. The runtime can spawn a certain number of worker threads at startup. These threads each have a work queue associated with them.

Consider the following trivial example:

```
uint32_t[100] array;

val top := 100;
val bot := 0;
val mid := top>>1;

var sortq := work_queue_t();

queue sort_half(array, top, mid) on sortq;
queue sort_half(array, mid-1, bot) on sortq;

dispatch sortq;

// ... other code
sort_half(uint32_t[] array, uint32_t top, uint32_t bot) 
	returns (uint32_t sorted_array)
{
 // ... do the sort, return the sorted array in sorted_array.
}
```


> This works by creating what are essentially local messages for the function calls. (metal supports message passing objects called protocols, much like Objective C.) The parameters are evaluated in place, just like a synchronous function call would, but instead of being pushed onto the stack they are converted into a message and stored in the work\_queue\_t structure.

> When dispatch is actually called, the main thread invokes a support function in the RTE that looks in the thread pool for free threads. For each free thread the function finds, it takes the queued job information and hands it over to the thread. The thread executes the job and stores the results, then goes back to sleep. When all jobs have been finished, the dispatcher returns and execution continues synchronously with the next instruction after the dispatch.

> The results can be retrieved by treating the work queue as an array.

```
val first_half := sortq[0].sorted_array;
val second_half := sortq[1].sorted_array;
```

> This sort of general parallelism can be used in a number of algorithms. One of the best features is that it doesn't clog your code up with a bunch of extraneous crud like creating threads in most languages does. As long as the functions do not mutate any variables except their outputs they are automatically reentrant. If other state is mutated you must take care to enclose it within the correct critical sections, just like any other shared-memory parallelism.

#### 10.2.1 Low level details ####

> The low-level details of this process are really quite straightforward. Any function call dispatched will cause the compiler to also generate a specialized message proxy that converts the message to a normal function call, and then back again. In fact, this is the same technique the compiler uses for creating and executing lambda expressions.

## 11 Object Caching (Struct and Protocol) ##

This provides some details regarding the caching mechanism that metal uses.

### 11.1 Slab ###

> A slab is allocated from the main system allocator. The slab size is (N\*S)+(N\*4)+4 where N is the number of objects to cache, and S is the size of the object. By default N is 32, although there is no reason this number couldn't be configurable.

> A slab looks like this:

```
struct slab_t
{
	@slab_t prev;
	uint8_t top;
	uint32_t[32] cache;
	the_type[32] slab;
};
```

Where “the\_type” is whatever type the slab is being optimized for. The members break down like this:

| Name             | Description              |
|:-----------------|:-------------------------|
| prev             | Points to the previous slab in the list. |
| top              | Points to the next full slot in the cache. |
| cache            | The list of memory locations in the slab used to hold the next available object. |
| slab             | The data area where the cache addresses are taken from. |

### 11.2 How it Works ###

The caching allocator looks at a global variable with a unique name for each type. That variable holds a pointer to the currently active slab. When an allocation occurs, the following steps take place:

  1. Get the currently active slab for the type.
  1. If there is no currently active slab, create one.
  1. If slab.top==32, it is full. Select the previous slab and repeat this step. If we get all the way back to the beginning, create a new slab and use it.
  1. Pull the next available address out of slab.cache[slab.top].
  1. Increment top.
  1. Return the address as the address to the new object.

> In the common case, steps 2 and 3 are skipped, leaving four fast, simple operations. In addition, each slab is per-type, so as to reduce processor interlock in multi-threaded programs.

The deallocation happens in a very similar process.

  1. Get the currently active slab for the type.
  1. If the slab is empty, possibly free it back to the system.
  1. If the address is not inside the current slab, choose the previous slab and repeat this step.
  1. Decrement top.
  1. Store the address at slab.cache[slab.top].

In the common case, step 3 does not have to recurse deeply. The metrics for deciding when to free a slab back to the system are not yet decided. However, there is one additional function that is important.


### 11.3 Garbage Collection ###

> As has been explained earlier, metal uses reference counting and immediate destruction, instead of a mark and sweep algorithm. While mark-and-sweep type algorithms are very nice for the programmer who has to deal with references, and can also very handily deal with cycles, they have a problem with “when.” On the other hand, reference counting semantics are very clear about when.

> Still, this object cache optimizing can commit a lot of memory that might not actually be used. In order to provide the system with the ability to reclaim empty slabs, each type also generates a garbage collection function. It implements the following algorithm:

  1. Get the currently active slab for the type. If there is none, we are done.
  1. If the slab is empty, store the pointer to the previous slab and return this slab to the system, otherwise go to step 4.
  1. Make the previous slab the currently active slab. Go to step 2.
  1. Get the pointer to the previous slab. prev:=cur\_slab.prev
  1. If it's empty, update the previous pointer of the current slab. (not the currently active slab). cur\_slab.prev=prev.prev; Otherwise, go to step 7.
  1. Free the previous slab by returning it to the system. Go to step 4.
  1. Set cur\_slab to the previous slab. cur\_slab:=cur\_slab.prev. If cur\_slab is not null, go to step 4. Otherwise we are done.



In other words, walk the slab list, freeing any empty slabs and adjusting the list as we go.

\<(var|val|protocol|returns|pass|fail|when|guarded|require|ensure|from|otherwise|import|properties|mutate|struct|operator)\>

## 12 Runtime Type Information ##


## 13 Tail Call Rules ##


Metal supports tail calls, and has very simple rules regarding them. A function block must end with one of the following:

  1. pass
  1. fail
  1. a call to itself

The last case is a tail call. When executing a tail call, the function will not “return” to itself. Instead, tail call will generated, which causes the function to simply jump back to the beginning of the function after updating the input parameters. A new stack frame is not generated.

### 13.1 Garbage collection ###

You might wonder, how does this interact with the automatic reference counting and garbage collection? The compiler follows this algorithm when generating code for a tail call:

  1. Evaluate all non-leaf parameters. (That is, if the parameter is an expression consisting of more than a literal or variable, evaluate it.)
  1. Perform end-of-block destruction for the current block and all parent blocks. (Decrement references to all objects referenced by variables or values created in this block. For any objects who's reference count drops to zero, free that object.
  1. Make the tail call. metal will either use the LLVM tail call mechanism, or the phi structure for performing the tail call.


This ensures that all local variables and parameters are freed properly before the tail call, but also that the parameters used as input into the tail call have valid references to any data that needs to go forward.