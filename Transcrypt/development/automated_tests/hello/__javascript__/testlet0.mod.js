	__nest__ (
		__all__,
		'testlet0', {
			__all__: {
				__inited__: false,
				__init__: function (__all__) {
					var run = function (autoTester) {
						autoTester.check ('hello');
						autoTester.check ('world');
					};
					//<all>
					__all__.run = run;
					//</all>
				}
			}
		}
	);