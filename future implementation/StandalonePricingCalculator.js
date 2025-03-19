import { useState, useEffect } from 'react'

export default function StandalonePricingCalculator() {
  // Node counts
  const [simpleNodeCount, setSimpleNodeCount] = useState(5);
  const [moderateNodeCount, setModerateNodeCount] = useState(7);
  const [complexNodeCount, setComplexNodeCount] = useState(3);
  
  // Make.com parameters - using 80k operations as default
  const [operationsPerMonth, setOperationsPerMonth] = useState('80000');
  const [activeScenariosCount, setActiveScenariosCount] = useState('5');
  const [makePlan, setMakePlan] = useState('pro');

  // Calculated values
  const [totalNodes, setTotalNodes] = useState(0);
  const [totalPrice, setTotalPrice] = useState(0);
  const [makeMonthlyCost, setMakeMonthlyCost] = useState(0);
  const [breakEvenMonths, setBreakEvenMonths] = useState(0);
  const [oneYearSavings, setOneYearSavings] = useState(0);

  // Calculate total nodes
  useEffect(() => {
    const total = simpleNodeCount + moderateNodeCount + complexNodeCount;
    setTotalNodes(total);
    
    // Calculate conversion price
    calculateConversionPrice();
  }, [simpleNodeCount, moderateNodeCount, complexNodeCount]);

  // Calculate Make.com monthly cost based on plan and usage
  const getMakeMonthlyCost = () => {
    const operations = parseInt(operationsPerMonth);
    const scenarios = parseInt(activeScenariosCount);
    
    let baseCost = 0;
    let opsIncluded = 0;
    let additionalOpsCost = 0;
    let scenariosIncluded = 0;
    let additionalScenariosCost = 0;
    
    // Set plan parameters
    switch(makePlan) {
      case 'core':
        baseCost = 9;
        opsIncluded = 10000;
        additionalOpsCost = 9;  // per 10k additional ops
        scenariosIncluded = 2;
        additionalScenariosCost = 5;  // per additional scenario
        break;
      case 'pro':
        baseCost = 16;
        opsIncluded = 25000;
        // Sliding scale - cost decreases as volume increases
        if (operations <= 25000) {
          additionalOpsCost = 8;  // per 10k additional ops for first tier
        } else if (operations <= 50000) {
          additionalOpsCost = 7.5;  // slightly less per 10k for second tier
        } else if (operations <= 100000) {
          additionalOpsCost = 7;  // even less per 10k for third tier
        } else {
          additionalOpsCost = 6.5;  // lowest rate for highest volume
        }
        scenariosIncluded = 5;
        additionalScenariosCost = 4;  // per additional scenario
        break;
      case 'team':
        baseCost = 29;
        opsIncluded = 50000;
        // Sliding scale - cost decreases as volume increases
        if (operations <= 50000) {
          additionalOpsCost = 7;  // per 10k additional ops for first tier
        } else if (operations <= 100000) {
          additionalOpsCost = 6.5;  // slightly less per 10k for second tier
        } else if (operations <= 200000) {
          additionalOpsCost = 6;  // even less per 10k for third tier
        } else {
          additionalOpsCost = 5.5;  // lowest rate for highest volume
        }
        scenariosIncluded = 15;
        additionalScenariosCost = 3;  // per additional scenario
        break;
      case 'enterprise':
        baseCost = 199;
        opsIncluded = 200000;
        additionalOpsCost = 6;  // per 10k additional ops
        scenariosIncluded = 50;
        additionalScenariosCost = 2;  // per additional scenario
        break;
      default:
        baseCost = 16;
        opsIncluded = 25000;
        additionalOpsCost = 8;
        scenariosIncluded = 5;
        additionalScenariosCost = 4;
    }
    
    // Calculate additional operations cost
    const additionalOps = Math.max(0, operations - opsIncluded);
    const additionalOpsBlocks = Math.ceil(additionalOps / 10000);
    const totalAdditionalOpsCost = additionalOpsBlocks * additionalOpsCost;
    
    // Calculate additional scenarios cost
    const additionalScenarios = Math.max(0, scenarios - scenariosIncluded);
    const totalAdditionalScenariosCost = additionalScenarios * additionalScenariosCost;
    
    // Calculate total monthly cost
    return baseCost + totalAdditionalOpsCost + totalAdditionalScenariosCost;
  };

  // Calculate conversion price based on node counts
  const calculateConversionPrice = () => {
    const nodeCategories = [
      { count: simpleNodeCount, basePrice: 20 },
      { count: moderateNodeCount, basePrice: 25 },
      { count: complexNodeCount, basePrice: 30 }
    ];

    // Apply volume discounts
    let totalCost = 0;
    let processedNodes = 0;
    
    for (const category of nodeCategories) {
      let remainingInCategory = category.count;
      let nodesToProcess = remainingInCategory;
      
      // First 10 nodes - standard pricing
      const tier1Count = Math.min(10 - processedNodes, nodesToProcess);
      if (tier1Count > 0) {
        totalCost += tier1Count * category.basePrice;
        nodesToProcess -= tier1Count;
        processedNodes += tier1Count;
      }
      
      // Nodes 11-30 - 25% discount
      const tier2Count = Math.min(30 - processedNodes, nodesToProcess);
      if (tier2Count > 0) {
        totalCost += tier2Count * (category.basePrice * 0.75);
        nodesToProcess -= tier2Count;
        processedNodes += tier2Count;
      }
      
      // Nodes 31-50 - 50% discount
      const tier3Count = Math.min(50 - processedNodes, nodesToProcess);
      if (tier3Count > 0) {
        totalCost += tier3Count * (category.basePrice * 0.5);
        nodesToProcess -= tier3Count;
        processedNodes += tier3Count;
      }
      
      // Nodes 51+ - 70% discount
      if (nodesToProcess > 0) {
        totalCost += nodesToProcess * (category.basePrice * 0.3);
        processedNodes += nodesToProcess;
      }
    }
    
    setTotalPrice(Math.round(totalCost));
    calculateBreakeven(Math.round(totalCost));
  };

  // Calculate breakeven point and savings
  const calculateBreakeven = (conversionCost) => {
    const monthlyMakeCost = getMakeMonthlyCost();
    setMakeMonthlyCost(monthlyMakeCost);
    
    // Calculate break-even in months (rounded up)
    const breakEven = Math.ceil(conversionCost / monthlyMakeCost);
    setBreakEvenMonths(breakEven);
    
    // Calculate 1-year savings
    const savings = (monthlyMakeCost * 12) - conversionCost;
    setOneYearSavings(savings);
  };

  // Recalculate whenever inputs change
  useEffect(() => {
    calculateBreakeven(totalPrice);
  }, [operationsPerMonth, activeScenariosCount, makePlan, totalPrice]);

  return (
    <div className="bg-white rounded-lg p-6 mt-4">
      <div className="max-w-4xl mx-auto">
        <p className="text-center text-gray-600 mb-8">Enter your estimated node counts and see how quickly you'll break even with n8n</p>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-6">
        <div>
          <h3 className="text-lg font-semibold mb-4">Workflow Configuration</h3>
          
          <div className="mb-4 bg-gray-50 rounded-lg p-4 border border-gray-200">
            <div className="flex items-center justify-between mb-1">
              <label htmlFor="simpleNodeCount" className="block text-sm font-semibold text-gray-700">
                Simple Nodes ($20 each)
              </label>
              <span className="text-xs text-gray-500">HTTP requests, simple transformations</span>
            </div>
            <div className="flex items-center">
              <button 
                className="px-3 py-2 bg-gray-200 rounded-l-md text-gray-700 hover:bg-gray-300 font-bold"
                onClick={() => setSimpleNodeCount(Math.max(0, simpleNodeCount - 1))}
              >
                –
              </button>
              <input
                type="number"
                id="simpleNodeCount"
                className="w-20 text-center border-gray-300 focus:border-primary focus:ring-primary py-2"
                value={simpleNodeCount}
                onChange={(e) => setSimpleNodeCount(parseInt(e.target.value) || 0)}
                min="0"
              />
              <button 
                className="px-3 py-2 bg-gray-200 rounded-r-md text-gray-700 hover:bg-gray-300 font-bold"
                onClick={() => setSimpleNodeCount(simpleNodeCount + 1)}
              >
                +
              </button>
            </div>
          </div>
          
          <div className="mb-4 bg-gray-50 rounded-lg p-4 border border-gray-200">
            <div className="flex items-center justify-between mb-1">
              <label htmlFor="moderateNodeCount" className="block text-sm font-semibold text-gray-700">
                Moderate Nodes ($25 each)
              </label>
              <span className="text-xs text-gray-500">API integrations, data processing</span>
            </div>
            <div className="flex items-center">
              <button 
                className="px-3 py-2 bg-gray-200 rounded-l-md text-gray-700 hover:bg-gray-300 font-bold"
                onClick={() => setModerateNodeCount(Math.max(0, moderateNodeCount - 1))}
              >
                –
              </button>
              <input
                type="number"
                id="moderateNodeCount"
                className="w-20 text-center border-gray-300 focus:border-primary focus:ring-primary py-2"
                value={moderateNodeCount}
                onChange={(e) => setModerateNodeCount(parseInt(e.target.value) || 0)}
                min="0"
              />
              <button 
                className="px-3 py-2 bg-gray-200 rounded-r-md text-gray-700 hover:bg-gray-300 font-bold"
                onClick={() => setModerateNodeCount(moderateNodeCount + 1)}
              >
                +
              </button>
            </div>
          </div>
          
          <div className="mb-4 bg-gray-50 rounded-lg p-4 border border-gray-200">
            <div className="flex items-center justify-between mb-1">
              <label htmlFor="complexNodeCount" className="block text-sm font-semibold text-gray-700">
                Complex Nodes ($30 each)
              </label>
              <span className="text-xs text-gray-500">Advanced integrations, custom logic</span>
            </div>
            <div className="flex items-center">
              <button 
                className="px-3 py-2 bg-gray-200 rounded-l-md text-gray-700 hover:bg-gray-300 font-bold"
                onClick={() => setComplexNodeCount(Math.max(0, complexNodeCount - 1))}
              >
                –
              </button>
              <input
                type="number"
                id="complexNodeCount"
                className="w-20 text-center border-gray-300 focus:border-primary focus:ring-primary py-2"
                value={complexNodeCount}
                onChange={(e) => setComplexNodeCount(parseInt(e.target.value) || 0)}
                min="0"
              />
              <button 
                className="px-3 py-2 bg-gray-200 rounded-r-md text-gray-700 hover:bg-gray-300 font-bold"
                onClick={() => setComplexNodeCount(complexNodeCount + 1)}
              >
                +
              </button>
            </div>
          </div>
          
          <div className="mt-6">
            <div className="p-4 bg-gray-50 rounded-lg border border-gray-200">
              <div className="flex justify-between">
                <span className="font-medium">Total Nodes:</span>
                <span className="font-bold text-lg">{totalNodes}</span>
              </div>
              <div className="flex justify-between mt-2">
                <span className="font-medium">Estimated Conversion Cost:</span>
                <span className="font-bold text-xl text-primary">${totalPrice}</span>
              </div>
            </div>
          </div>
        </div>
        
        <div className="bg-gradient-to-r from-blue-50 to-green-50 rounded-lg p-5 border border-blue-100">
          <h3 className="text-lg font-semibold mb-4 text-gray-800">Make.com Subscription Costs</h3>
          
          <div className="mb-4">
            <label htmlFor="operationsPerMonth" className="block text-sm font-medium text-gray-700 mb-1">
              Monthly Operations
            </label>
            <select 
              id="operationsPerMonth" 
              className="w-full border-gray-300 rounded-md px-3 py-2 focus:border-primary focus:ring-primary"
              value={operationsPerMonth}
              onChange={(e) => setOperationsPerMonth(e.target.value)}
            >
              <option value="10000">10,000 ops/month</option>
              <option value="25000">25,000 ops/month</option>
              <option value="50000">50,000 ops/month</option>
              <option value="80000">80,000 ops/month (Average)</option>
              <option value="100000">100,000 ops/month</option>
              <option value="200000">200,000 ops/month</option>
              <option value="500000">500,000 ops/month</option>
            </select>
          </div>
          
          <div className="mb-4">
            <label htmlFor="activeScenariosCount" className="block text-sm font-medium text-gray-700 mb-1">
              Active Scenarios
            </label>
            <select 
              id="activeScenariosCount" 
              className="w-full border-gray-300 rounded-md px-3 py-2 focus:border-primary focus:ring-primary"
              value={activeScenariosCount}
              onChange={(e) => setActiveScenariosCount(e.target.value)}
            >
              <option value="1">1 scenario</option>
              <option value="2">2 scenarios</option>
              <option value="5">5 scenarios</option>
              <option value="10">10 scenarios</option>
              <option value="15">15 scenarios</option>
              <option value="25">25 scenarios</option>
              <option value="50">50 scenarios</option>
            </select>
          </div>
          
          <div className="mb-4">
            <label htmlFor="makePlan" className="block text-sm font-medium text-gray-700 mb-1">
              Make.com Plan
            </label>
            <select 
              id="makePlan" 
              className="w-full border-gray-300 rounded-md px-3 py-2 focus:border-primary focus:ring-primary"
              value={makePlan}
              onChange={(e) => setMakePlan(e.target.value)}
            >
              <option value="core">Core ($9/mo)</option>
              <option value="pro">Pro ($16/mo)</option>
              <option value="team">Team ($29/mo)</option>
              <option value="enterprise">Enterprise ($199/mo)</option>
            </select>
          </div>
          
          <div className="mt-6 p-4 bg-green-50 rounded-lg border-2 border-green-200 shadow-md">
            <h4 className="font-medium text-green-800 mb-2 text-center text-lg">Your Savings</h4>
            
            <div className="mb-4">
              <div className="flex justify-between text-sm mb-1">
                <span className="font-medium">Estimated Make.com monthly cost:</span>
                <span className="font-bold">
                  ${makeMonthlyCost}
                </span>
              </div>
              
              <div className="flex justify-between text-sm">
                <span className="font-medium">n8n self-hosted monthly cost:</span>
                <span className="font-bold">$0</span>
              </div>
            </div>
            
            <div className="bg-white p-4 rounded-lg border-2 border-green-100 mt-4 shadow-sm">
              <div className="text-center">
                <div className="mb-3">
                  <span className="font-medium text-gray-700">Break-even after:</span>
                  <span className="block text-3xl font-bold text-green-600 my-2">{breakEvenMonths} months</span>
                </div>
                
                <div className="pt-2 border-t border-gray-100">
                  <span className="font-medium text-gray-700">First year savings:</span>
                  <span className="block text-2xl font-bold text-green-600 my-2">${oneYearSavings}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <div className="mt-8 text-center">
        <a href="mailto:info@spotcircuit.com?subject=Workflow%20Conversion%20Inquiry" 
           className="inline-block bg-primary text-white px-6 py-3 rounded-md font-medium hover:bg-primary-dark transition-colors duration-200">
          Get Started with Your Conversion
        </a>
      </div>
      </div>
    </div>
  );
}
