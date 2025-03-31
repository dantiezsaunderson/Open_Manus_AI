"""
Enhanced Multi-Agent System Module

This module implements an improved collaborative multi-agent system for task delegation
and specialized processing in the Open Manus AI system, with enhanced financial capabilities.
"""

import logging
import uuid
import threading
import queue
import time
import json
from datetime import datetime

# Configure logging
logger = logging.getLogger(__name__)

class EnhancedAgent:
    """Enhanced base class for specialized agents in the multi-agent system."""
    
    def __init__(self, name, agent_type, ai_engine=None):
        """
        Initialize a specialized agent.
        
        Args:
            name (str): Agent name
            agent_type (str): Type of agent (e.g., 'research', 'coding', 'financial')
            ai_engine (AIEngine, optional): AI engine instance for the agent
        """
        self.id = str(uuid.uuid4())
        self.name = name
        self.type = agent_type
        self.ai_engine = ai_engine
        self.task_queue = queue.Queue()
        self.results = {}
        self.running = False
        self.worker_thread = None
        self.status = "initialized"
        self.progress = 0
        logger.info(f"Agent '{name}' ({agent_type}) initialized")
    
    def start(self):
        """Start the agent's worker thread."""
        if not self.running:
            self.running = True
            self.status = "running"
            self.worker_thread = threading.Thread(target=self._process_tasks, daemon=True)
            self.worker_thread.start()
            logger.info(f"Agent '{self.name}' started")
    
    def stop(self):
        """Stop the agent's worker thread."""
        if self.running:
            self.running = False
            self.status = "stopped"
            if self.worker_thread:
                self.worker_thread.join(timeout=2.0)
            logger.info(f"Agent '{self.name}' stopped")
    
    def assign_task(self, task):
        """
        Assign a task to this agent.
        
        Args:
            task (dict): Task definition
            
        Returns:
            str: Task ID
        """
        task_id = task.get('id', str(uuid.uuid4()))
        task['id'] = task_id
        task['status'] = 'assigned'
        task['assigned_time'] = time.time()
        task['progress'] = 0
        
        self.task_queue.put(task)
        self.results[task_id] = {
            'status': 'pending',
            'progress': 0,
            'assigned_time': datetime.now().isoformat()
        }
        
        logger.info(f"Task {task_id} assigned to agent '{self.name}'")
        return task_id
    
    def get_result(self, task_id):
        """
        Get the result of a task.
        
        Args:
            task_id (str): Task ID
            
        Returns:
            dict: Task result or status
        """
        return self.results.get(task_id, {'status': 'unknown'})
    
    def get_status(self):
        """
        Get the current status of the agent.
        
        Returns:
            dict: Agent status information
        """
        return {
            'id': self.id,
            'name': self.name,
            'type': self.type,
            'status': self.status,
            'progress': self.progress,
            'queue_size': self.task_queue.qsize(),
            'active_tasks': sum(1 for result in self.results.values() if result.get('status') in ['pending', 'processing'])
        }
    
    def update_progress(self, task_id, progress, status_message=None):
        """
        Update the progress of a task.
        
        Args:
            task_id (str): Task ID
            progress (float): Progress value (0-100)
            status_message (str, optional): Status message
        """
        if task_id in self.results:
            self.results[task_id]['progress'] = progress
            if status_message:
                self.results[task_id]['status_message'] = status_message
            logger.debug(f"Task {task_id} progress updated: {progress}%")
    
    def _process_tasks(self):
        """Process tasks from the queue (to be implemented by subclasses)."""
        while self.running:
            try:
                if not self.task_queue.empty():
                    task = self.task_queue.get()
                    logger.info(f"Agent '{self.name}' processing task {task['id']}")
                    
                    try:
                        # Update task status
                        task['status'] = 'processing'
                        self.results[task['id']] = {
                            'status': 'processing',
                            'progress': 0,
                            'start_time': datetime.now().isoformat()
                        }
                        
                        # Process the task (to be implemented by subclasses)
                        result = self._execute_task(task)
                        
                        # Store the result
                        self.results[task['id']] = {
                            'status': 'completed',
                            'result': result,
                            'progress': 100,
                            'completion_time': datetime.now().isoformat()
                        }
                        
                        logger.info(f"Agent '{self.name}' completed task {task['id']}")
                        
                    except Exception as e:
                        logger.error(f"Error processing task {task['id']}: {e}")
                        self.results[task['id']] = {
                            'status': 'failed',
                            'error': str(e),
                            'completion_time': datetime.now().isoformat()
                        }
                    
                    self.task_queue.task_done()
                else:
                    # Sleep briefly to avoid busy waiting
                    time.sleep(0.1)
                    
            except Exception as e:
                logger.error(f"Error in agent '{self.name}' task processing: {e}")
                time.sleep(1)  # Avoid rapid error loops
    
    def _execute_task(self, task):
        """
        Execute a task (to be implemented by subclasses).
        
        Args:
            task (dict): Task definition
            
        Returns:
            dict: Task execution result
        """
        raise NotImplementedError("Subclasses must implement _execute_task")


class EnhancedResearchAgent(EnhancedAgent):
    """Enhanced specialized agent for research and information gathering."""
    
    def __init__(self, ai_engine):
        """Initialize a research agent."""
        super().__init__("Research Agent", "research", ai_engine)
    
    def _execute_task(self, task):
        """Execute a research task."""
        task_type = task.get('task_type', 'general')
        query = task.get('query', '')
        
        if not query:
            return {'error': 'No query provided'}
        
        # Update progress
        self.update_progress(task['id'], 10, "Starting research")
        
        if task_type == 'summarize':
            system_message = "You are a research assistant. Summarize the following information concisely but thoroughly."
            self.update_progress(task['id'], 30, "Generating summary")
            result = self.ai_engine.generate_response(query, system_message=system_message)
            self.update_progress(task['id'], 90, "Summary generated")
            return {'summary': result}
        
        elif task_type == 'analyze':
            system_message = "You are a research analyst. Analyze the following information and provide insights."
            self.update_progress(task['id'], 30, "Analyzing information")
            result = self.ai_engine.generate_response(query, system_message=system_message)
            self.update_progress(task['id'], 90, "Analysis completed")
            return {'analysis': result}
        
        else:  # general research
            system_message = "You are a research assistant. Provide comprehensive information on the following topic."
            self.update_progress(task['id'], 30, "Researching topic")
            result = self.ai_engine.generate_response(query, system_message=system_message)
            self.update_progress(task['id'], 90, "Research completed")
            return {'research': result}


class EnhancedCodingAgent(EnhancedAgent):
    """Enhanced specialized agent for coding and software development."""
    
    def __init__(self, ai_engine):
        """Initialize a coding agent."""
        super().__init__("Coding Agent", "coding", ai_engine)
    
    def _execute_task(self, task):
        """Execute a coding task."""
        task_type = task.get('task_type', 'generate')
        language = task.get('language', 'python')
        code = task.get('code', '')
        prompt = task.get('prompt', '')
        
        # Update progress
        self.update_progress(task['id'], 10, f"Starting {task_type} task")
        
        if task_type == 'generate':
            if not prompt:
                return {'error': 'No prompt provided for code generation'}
            
            system_message = f"You are an expert {language} programmer. Generate clean, efficient code based on the requirements."
            self.update_progress(task['id'], 30, "Generating code")
            result = self.ai_engine.generate_response(prompt, system_message=system_message)
            
            # Extract code from result
            import re
            code_pattern = f"```{language}(.*?)```"
            code_match = re.search(code_pattern, result, re.DOTALL)
            
            self.update_progress(task['id'], 90, "Code generated")
            
            if code_match:
                extracted_code = code_match.group(1).strip()
                return {'code': extracted_code, 'explanation': result}
            else:
                return {'code': '', 'explanation': result}
        
        elif task_type == 'analyze':
            if not code:
                return {'error': 'No code provided for analysis'}
            
            system_message = f"You are a code review expert. Analyze this {language} code and provide feedback on quality, bugs, and improvements."
            self.update_progress(task['id'], 30, "Analyzing code")
            result = self.ai_engine.generate_response(code, system_message=system_message)
            self.update_progress(task['id'], 90, "Code analysis completed")
            return {'analysis': result}
        
        elif task_type == 'refactor':
            if not code:
                return {'error': 'No code provided for refactoring'}
            
            system_message = f"You are a code refactoring expert. Improve this {language} code while maintaining its functionality."
            self.update_progress(task['id'], 30, "Refactoring code")
            result = self.ai_engine.generate_response(code, system_message=system_message)
            
            # Extract code from result
            import re
            code_pattern = f"```{language}(.*?)```"
            code_match = re.search(code_pattern, result, re.DOTALL)
            
            self.update_progress(task['id'], 90, "Code refactored")
            
            if code_match:
                refactored_code = code_match.group(1).strip()
                return {'refactored_code': refactored_code, 'explanation': result}
            else:
                return {'refactored_code': '', 'explanation': result}
        
        else:
            return {'error': f'Unknown task type: {task_type}'}


class EnhancedFinancialAgent(EnhancedAgent):
    """Enhanced specialized agent for financial analysis and recommendations."""
    
    def __init__(self, ai_engine, financial_analysis_module=None):
        """
        Initialize a financial agent.
        
        Args:
            ai_engine (AIEngine): AI engine instance
            financial_analysis_module (EnhancedFinancialAnalysisModule, optional): Financial analysis module
        """
        super().__init__("Financial Agent", "financial", ai_engine)
        self.financial_analysis_module = financial_analysis_module
    
    def _execute_task(self, task):
        """Execute a financial analysis task."""
        task_type = task.get('task_type', 'analyze')
        symbol = task.get('symbol', '')
        data = task.get('data', '')
        period = task.get('period', '1mo')
        
        # Update initial progress
        self.update_progress(task['id'], 10, f"Starting {task_type} task")
        
        if not self.financial_analysis_module:
            return {'error': 'Financial analysis module not available'}
        
        if task_type == 'analyze_stock':
            if not symbol:
                return {'error': 'No stock symbol provided'}
            
            self.update_progress(task['id'], 30, f"Analyzing stock {symbol}")
            analysis = self.financial_analysis_module.analyze_stock(symbol)
            self.update_progress(task['id'], 90, "Stock analysis completed")
            return analysis
        
        elif task_type == 'get_stock_data':
            if not symbol:
                return {'error': 'No stock symbol provided'}
            
            self.update_progress(task['id'], 30, f"Retrieving stock data for {symbol}")
            stock_data = self.financial_analysis_module.get_stock_data(symbol, period=period)
            self.update_progress(task['id'], 90, "Stock data retrieved")
            return stock_data
        
        elif task_type == 'generate_chart':
            if not symbol:
                return {'error': 'No stock symbol provided'}
            
            chart_type = task.get('chart_type', 'line')
            include_volume = task.get('include_volume', True)
            include_indicators = task.get('include_indicators', False)
            
            self.update_progress(task['id'], 30, f"Generating chart for {symbol}")
            chart = self.financial_analysis_module.generate_stock_chart(
                symbol, 
                period=period, 
                chart_type=chart_type,
                include_volume=include_volume,
                include_indicators=include_indicators
            )
            self.update_progress(task['id'], 90, "Chart generated")
            return chart
        
        elif task_type == 'get_fundamentals':
            if not symbol:
                return {'error': 'No stock symbol provided'}
            
            self.update_progress(task['id'], 30, f"Retrieving fundamentals for {symbol}")
            fundamentals = self.financial_analysis_module.get_company_fundamentals(symbol)
            self.update_progress(task['id'], 90, "Fundamentals retrieved")
            return fundamentals
        
        elif task_type == 'get_insider_trading':
            if not symbol:
                return {'error': 'No stock symbol provided'}
            
            self.update_progress(task['id'], 30, f"Retrieving insider trading data for {symbol}")
            insider_data = self.financial_analysis_module.get_insider_trading(symbol)
            self.update_progress(task['id'], 90, "Insider trading data retrieved")
            return insider_data
        
        elif task_type == 'get_sec_filings':
            if not symbol:
                return {'error': 'No stock symbol provided'}
            
            self.update_progress(task['id'], 30, f"Retrieving SEC filings for {symbol}")
            filings = self.financial_analysis_module.get_sec_filings(symbol)
            self.update_progress(task['id'], 90, "SEC filings retrieved")
            return filings
        
        elif task_type == 'get_analyst_opinions':
            if not symbol:
                return {'error': 'No stock symbol provided'}
            
            self.update_progress(task['id'], 30, f"Retrieving analyst opinions for {symbol}")
            opinions = self.financial_analysis_module.get_analyst_opinions(symbol)
            self.update_progress(task['id'], 90, "Analyst opinions retrieved")
            return opinions
        
        elif task_type == 'analyze_portfolio':
            portfolio = task.get('portfolio', [])
            if not portfolio:
                return {'error': 'No portfolio data provided'}
            
            self.update_progress(task['id'], 30, "Analyzing portfolio")
            portfolio_analysis = self.financial_analysis_module.analyze_portfolio(portfolio)
            self.update_progress(task['id'], 90, "Portfolio analysis completed")
            return portfolio_analysis
        
        elif task_type == 'analyze_text':
            if not data:
                return {'error': 'No financial text provided for analysis'}
            
            system_message = "You are a financial analyst. Analyze the following financial information and provide insights."
            self.update_progress(task['id'], 30, "Analyzing financial text")
            result = self.ai_engine.analyze_financial_data(data)
            self.update_progress(task['id'], 90, "Financial text analysis completed")
            return result
        
        else:
            return {'error': f'Unknown task type: {task_type}'}


class StockScreenerAgent(EnhancedFinancialAgent):
    """Specialized agent for stock screening and filtering."""
    
    def __init__(self, ai_engine, financial_analysis_module=None):
        """Initialize a stock screener agent."""
        super().__init__(ai_engine, financial_analysis_module)
        self.name = "Stock Screener Agent"
        self.type = "stock_screener"
    
    def _execute_task(self, task):
        """Execute a stock screening task."""
        task_type = task.get('task_type', 'screen')
        criteria = task.get('criteria', {})
        symbols = task.get('symbols', [])
        
        # Update initial progress
        self.update_progress(task['id'], 10, "Starting stock screening")
        
        if not self.financial_analysis_module:
            return {'error': 'Financial analysis module not available'}
        
        if task_type == 'screen':
            if not criteria:
                return {'error': 'No screening criteria provided'}
            
            if not symbols:
                # In a real implementation, we would get a list of symbols from a database or API
                return {'error': 'No symbols provided for screening'}
            
            self.update_progress(task['id'], 20, "Retrieving stock data for screening")
            
            # Process each symbol
            results = []
            total_symbols = len(symbols)
            
            for i, symbol in enumerate(symbols):
                # Update progress based on how many symbols we've processed
                progress = 20 + (i / total_symbols) * 70
                self.update_progress(task['id'], progress, f"Screening {symbol} ({i+1}/{total_symbols})")
                
                try:
                    # Get stock data and fundamentals
                    stock_data = self.financial_analysis_module.get_stock_data(symbol)
                    fundamentals = self.financial_analysis_module.get_company_fundamentals(symbol)
                    
                    # Check if the stock meets the criteria
                    meets_criteria = self._check_criteria(stock_data, fundamentals, criteria)
                    
                    if meets_criteria:
                        results.append({
                            'symbol': symbol,
                            'data': stock_data,
                            'fundamentals': fundamentals
                        })
                except Exception as e:
                    logger.warning(f"Error screening {symbol}: {e}")
            
            self.update_progress(task['id'], 90, "Screening completed")
            
            return {
                'success': True,
                'matches': results,
                'total_screened': total_symbols,
                'total_matches': len(results)
            }
        
        else:
            return {'error': f'Unknown task type: {task_type}'}
    
    def _check_criteria(self, stock_data, fundamentals, criteria):
        """
        Check if a stock meets the specified criteria.
        
        Args:
            stock_data (dict): Stock data
            fundamentals (dict): Fundamental data
            criteria (dict): Screening criteria
            
        Returns:
            bool: Whether the stock meets the criteria
        """
        # This is a simplified implementation
        # In a real implementation, this would be much more comprehensive
        
        if not stock_data.get('success', False) or not fundamentals.get('success', False):
            return False
        
        # Check price criteria
        if 'min_price' in criteria and stock_data.get('stats', {}).get('latest_price', 0) < criteria['min_price']:
            return False
        
        if 'max_price' in criteria and stock_data.get('stats', {}).get('latest_price', 0) > criteria['max_price']:
            return False
        
        # Check performance criteria
        if 'min_performance' in criteria:
            period = criteria.get('performance_period', '1mo')
            performance = stock_data.get('performance', {}).get(period, {}).get('change_pct', 0)
            if performance < criteria['min_performance']:
                return False
        
        # More criteria checks would be implemented here
        
        return True


class TechnicalAnalysisAgent(EnhancedFinancialAgent):
    """Specialized agent for technical analysis of stocks."""
    
    def __init__(self, ai_engine, financial_analysis_module=None):
        """Initialize a technical analysis agent."""
        super().__init__(ai_engine, financial_analysis_module)
        self.name = "Technical Analysis Agent"
        self.type = "technical_analysis"
    
    def _execute_task(self, task):
        """Execute a technical analysis task."""
        task_type = task.get('task_type', 'analyze')
        symbol = task.get('symbol', '')
        indicators = task.get('indicators', [])
        period = task.get('period', '6mo')
        
        # Update initial progress
        self.update_progress(task['id'], 10, "Starting technical analysis")
        
        if not self.financial_analysis_module:
            return {'error': 'Financial analysis module not available'}
        
        if not symbol:
            return {'error': 'No stock symbol provided'}
        
        if task_type == 'analyze':
            self.update_progress(task['id'], 30, f"Retrieving data for {symbol}")
            
            # Get stock data
            stock_data = self.financial_analysis_module.get_stock_data(symbol, period=period)
            
            if not stock_data.get('success', False):
                return {'error': f'Failed to retrieve stock data for {symbol}'}
            
            self.update_progress(task['id'], 50, "Calculating technical indicators")
            
            # Calculate technical indicators
            analysis_results = self._calculate_indicators(stock_data, indicators)
            
            self.update_progress(task['id'], 70, "Generating analysis report")
            
            # Generate analysis summary using AI
            if analysis_results and self.ai_engine:
                summary_prompt = f"Provide a technical analysis summary for {symbol} based on the following indicators: {json.dumps(analysis_results)}"
                system_message = "You are a technical analysis expert. Provide a concise but thorough analysis of the stock based on the technical indicators."
                summary = self.ai_engine.generate_response(summary_prompt, system_message=system_message)
                analysis_results['summary'] = summary
            
            self.update_progress(task['id'], 90, "Technical analysis completed")
            
            return {
                'success': True,
                'symbol': symbol,
                'period': period,
                'analysis': analysis_results
            }
        
        elif task_type == 'generate_chart':
            chart_type = task.get('chart_type', 'line')
            
            self.update_progress(task['id'], 30, f"Generating technical chart for {symbol}")
            
            # Generate chart with indicators
            chart = self.financial_analysis_module.generate_stock_chart(
                symbol, 
                period=period, 
                chart_type=chart_type,
                include_volume=True,
                include_indicators=True
            )
            
            self.update_progress(task['id'], 90, "Technical chart generated")
            
            return chart
        
        else:
            return {'error': f'Unknown task type: {task_type}'}
    
    def _calculate_indicators(self, stock_data, requested_indicators=None):
        """
        Calculate technical indicators for a stock.
        
        Args:
            stock_data (dict): Stock data
            requested_indicators (list, optional): List of indicators to calculate
            
        Returns:
            dict: Calculated indicators
        """
        # This is a simplified implementation
        # In a real implementation, this would use a library like ta-lib
        
        if not stock_data.get('success', False) or 'data' not in stock_data:
            return {}
        
        # Convert to DataFrame
        df = pd.DataFrame(stock_data['data'])
        
        # Ensure we have the necessary columns
        if 'close' not in df.columns:
            return {}
        
        # Default indicators if none specified
        if not requested_indicators:
            requested_indicators = ['sma', 'ema', 'rsi', 'macd', 'bollinger']
        
        results = {}
        
        # Calculate Simple Moving Averages
        if 'sma' in requested_indicators:
            sma_periods = [20, 50, 200]
            sma_results = {}
            
            for period in sma_periods:
                if len(df) >= period:
                    df[f'SMA{period}'] = df['close'].rolling(window=period).mean()
                    latest_sma = df[f'SMA{period}'].iloc[-1] if not df.empty else None
                    latest_close = df['close'].iloc[-1] if not df.empty else None
                    
                    if latest_sma is not None and latest_close is not None:
                        position = 'above' if latest_close > latest_sma else 'below'
                        signal = 'bullish' if latest_close > latest_sma else 'bearish'
                        
                        sma_results[f'SMA{period}'] = {
                            'value': latest_sma,
                            'position': position,
                            'signal': signal
                        }
            
            results['sma'] = sma_results
        
        # Calculate Exponential Moving Averages
        if 'ema' in requested_indicators:
            ema_periods = [12, 26, 50]
            ema_results = {}
            
            for period in ema_periods:
                if len(df) >= period:
                    df[f'EMA{period}'] = df['close'].ewm(span=period, adjust=False).mean()
                    latest_ema = df[f'EMA{period}'].iloc[-1] if not df.empty else None
                    latest_close = df['close'].iloc[-1] if not df.empty else None
                    
                    if latest_ema is not None and latest_close is not None:
                        position = 'above' if latest_close > latest_ema else 'below'
                        signal = 'bullish' if latest_close > latest_ema else 'bearish'
                        
                        ema_results[f'EMA{period}'] = {
                            'value': latest_ema,
                            'position': position,
                            'signal': signal
                        }
            
            results['ema'] = ema_results
        
        # Calculate RSI
        if 'rsi' in requested_indicators and len(df) >= 14:
            try:
                # Calculate daily returns
                df['returns'] = df['close'].pct_change()
                
                # Calculate gains and losses
                df['gain'] = np.where(df['returns'] > 0, df['returns'], 0)
                df['loss'] = np.where(df['returns'] < 0, -df['returns'], 0)
                
                # Calculate average gains and losses over 14 periods
                avg_gain = df['gain'].rolling(window=14).mean()
                avg_loss = df['loss'].rolling(window=14).mean()
                
                # Calculate RS and RSI
                rs = avg_gain / avg_loss
                df['RSI'] = 100 - (100 / (1 + rs))
                
                latest_rsi = df['RSI'].iloc[-1] if not df.empty and not pd.isna(df['RSI'].iloc[-1]) else None
                
                if latest_rsi is not None:
                    if latest_rsi < 30:
                        signal = 'oversold'
                    elif latest_rsi > 70:
                        signal = 'overbought'
                    else:
                        signal = 'neutral'
                    
                    results['rsi'] = {
                        'value': latest_rsi,
                        'signal': signal
                    }
            except Exception as e:
                logger.warning(f"Error calculating RSI: {e}")
        
        # Calculate MACD
        if 'macd' in requested_indicators and len(df) >= 26:
            try:
                # Calculate MACD components
                df['EMA12'] = df['close'].ewm(span=12, adjust=False).mean()
                df['EMA26'] = df['close'].ewm(span=26, adjust=False).mean()
                df['MACD'] = df['EMA12'] - df['EMA26']
                df['Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
                df['Histogram'] = df['MACD'] - df['Signal']
                
                latest_macd = df['MACD'].iloc[-1] if not df.empty else None
                latest_signal = df['Signal'].iloc[-1] if not df.empty else None
                latest_histogram = df['Histogram'].iloc[-1] if not df.empty else None
                
                if latest_macd is not None and latest_signal is not None:
                    signal = 'bullish' if latest_macd > latest_signal else 'bearish'
                    
                    # Check for crossovers
                    if len(df) >= 2:
                        prev_macd = df['MACD'].iloc[-2]
                        prev_signal = df['Signal'].iloc[-2]
                        
                        if prev_macd < prev_signal and latest_macd > latest_signal:
                            crossover = 'bullish'
                        elif prev_macd > prev_signal and latest_macd < latest_signal:
                            crossover = 'bearish'
                        else:
                            crossover = 'none'
                    else:
                        crossover = 'none'
                    
                    results['macd'] = {
                        'macd': latest_macd,
                        'signal': latest_signal,
                        'histogram': latest_histogram,
                        'trend': signal,
                        'crossover': crossover
                    }
            except Exception as e:
                logger.warning(f"Error calculating MACD: {e}")
        
        # Calculate Bollinger Bands
        if 'bollinger' in requested_indicators and len(df) >= 20:
            try:
                # Calculate 20-day SMA
                df['SMA20'] = df['close'].rolling(window=20).mean()
                
                # Calculate standard deviation
                df['STD20'] = df['close'].rolling(window=20).std()
                
                # Calculate Bollinger Bands
                df['UpperBand'] = df['SMA20'] + (df['STD20'] * 2)
                df['LowerBand'] = df['SMA20'] - (df['STD20'] * 2)
                
                latest_close = df['close'].iloc[-1] if not df.empty else None
                latest_upper = df['UpperBand'].iloc[-1] if not df.empty else None
                latest_lower = df['LowerBand'].iloc[-1] if not df.empty else None
                latest_middle = df['SMA20'].iloc[-1] if not df.empty else None
                
                if latest_close is not None and latest_upper is not None and latest_lower is not None:
                    if latest_close > latest_upper:
                        position = 'above_upper'
                        signal = 'overbought'
                    elif latest_close < latest_lower:
                        position = 'below_lower'
                        signal = 'oversold'
                    else:
                        position = 'within_bands'
                        signal = 'neutral'
                    
                    # Calculate bandwidth
                    bandwidth = (latest_upper - latest_lower) / latest_middle if latest_middle != 0 else 0
                    
                    results['bollinger'] = {
                        'upper': latest_upper,
                        'middle': latest_middle,
                        'lower': latest_lower,
                        'position': position,
                        'signal': signal,
                        'bandwidth': bandwidth
                    }
            except Exception as e:
                logger.warning(f"Error calculating Bollinger Bands: {e}")
        
        return results


class FundamentalAnalysisAgent(EnhancedFinancialAgent):
    """Specialized agent for fundamental analysis of stocks."""
    
    def __init__(self, ai_engine, financial_analysis_module=None):
        """Initialize a fundamental analysis agent."""
        super().__init__(ai_engine, financial_analysis_module)
        self.name = "Fundamental Analysis Agent"
        self.type = "fundamental_analysis"
    
    def _execute_task(self, task):
        """Execute a fundamental analysis task."""
        task_type = task.get('task_type', 'analyze')
        symbol = task.get('symbol', '')
        
        # Update initial progress
        self.update_progress(task['id'], 10, "Starting fundamental analysis")
        
        if not self.financial_analysis_module:
            return {'error': 'Financial analysis module not available'}
        
        if not symbol:
            return {'error': 'No stock symbol provided'}
        
        if task_type == 'analyze':
            self.update_progress(task['id'], 30, f"Retrieving fundamental data for {symbol}")
            
            # Get fundamental data
            fundamentals = self.financial_analysis_module.get_company_fundamentals(symbol)
            
            if not fundamentals.get('success', False):
                return {'error': f'Failed to retrieve fundamental data for {symbol}'}
            
            self.update_progress(task['id'], 50, "Analyzing financial statements")
            
            # Analyze financial statements
            analysis_results = self._analyze_fundamentals(fundamentals)
            
            self.update_progress(task['id'], 70, "Generating analysis report")
            
            # Generate analysis summary using AI
            if analysis_results and self.ai_engine:
                summary_prompt = f"Provide a fundamental analysis summary for {symbol} based on the following data: {json.dumps(analysis_results)}"
                system_message = "You are a financial analyst specializing in fundamental analysis. Provide a concise but thorough analysis of the company's financial health, growth prospects, and valuation."
                summary = self.ai_engine.generate_response(summary_prompt, system_message=system_message)
                analysis_results['summary'] = summary
            
            self.update_progress(task['id'], 90, "Fundamental analysis completed")
            
            return {
                'success': True,
                'symbol': symbol,
                'analysis': analysis_results
            }
        
        elif task_type == 'get_financial_statements':
            statement_type = task.get('statement_type', 'all')
            
            self.update_progress(task['id'], 30, f"Retrieving financial statements for {symbol}")
            
            # Get financial statements
            fundamentals = self.financial_analysis_module.get_company_fundamentals(symbol)
            
            if not fundamentals.get('success', False):
                return {'error': f'Failed to retrieve financial statements for {symbol}'}
            
            self.update_progress(task['id'], 90, "Financial statements retrieved")
            
            # Filter by statement type if specified
            if statement_type != 'all' and statement_type in fundamentals:
                return {
                    'success': True,
                    'symbol': symbol,
                    'statement_type': statement_type,
                    'data': fundamentals[statement_type]
                }
            
            return {
                'success': True,
                'symbol': symbol,
                'data': fundamentals
            }
        
        else:
            return {'error': f'Unknown task type: {task_type}'}
    
    def _analyze_fundamentals(self, fundamentals):
        """
        Analyze fundamental data for a company.
        
        Args:
            fundamentals (dict): Fundamental data
            
        Returns:
            dict: Analysis results
        """
        # This is a simplified implementation
        # In a real implementation, this would be much more comprehensive
        
        results = {
            'ratios': {},
            'growth': {},
            'valuation': {}
        }
        
        # Extract financial ratios if available
        if 'financial_ratios' in fundamentals and fundamentals['financial_ratios']:
            ratios = fundamentals['financial_ratios']
            
            # This would depend on the actual structure of the data
            # For now, we'll just pass through the ratios
            results['ratios'] = ratios
        
        # Calculate growth rates if income statements are available
        if 'income_statement' in fundamentals and fundamentals['income_statement']:
            income_statements = fundamentals['income_statement']
            
            # This would depend on the actual structure of the data
            # For now, we'll just note that we would calculate growth rates here
            results['growth']['revenue'] = 'Would calculate revenue growth here'
            results['growth']['earnings'] = 'Would calculate earnings growth here'
        
        # Calculate valuation metrics if we have the necessary data
        # This would require market data as well as financial statements
        results['valuation']['pe_ratio'] = 'Would calculate P/E ratio here'
        results['valuation']['price_to_book'] = 'Would calculate Price-to-Book ratio here'
        results['valuation']['price_to_sales'] = 'Would calculate Price-to-Sales ratio here'
        
        return results


class MultiAgentSystem:
    """Enhanced multi-agent system for coordinating specialized agents."""
    
    def __init__(self, ai_engine=None, financial_analysis_module=None):
        """
        Initialize the multi-agent system.
        
        Args:
            ai_engine (AIEngine, optional): AI engine instance
            financial_analysis_module (EnhancedFinancialAnalysisModule, optional): Financial analysis module
        """
        self.ai_engine = ai_engine
        self.financial_analysis_module = financial_analysis_module
        self.agents = {}
        self.task_assignments = {}
        logger.info("Multi-Agent System initialized")
    
    def register_agent(self, agent):
        """
        Register an agent with the system.
        
        Args:
            agent (EnhancedAgent): Agent to register
            
        Returns:
            str: Agent ID
        """
        self.agents[agent.id] = agent
        logger.info(f"Agent '{agent.name}' registered with ID {agent.id}")
        return agent.id
    
    def get_agent(self, agent_id):
        """
        Get an agent by ID.
        
        Args:
            agent_id (str): Agent ID
            
        Returns:
            EnhancedAgent: Agent instance or None if not found
        """
        return self.agents.get(agent_id)
    
    def get_agent_by_type(self, agent_type):
        """
        Get an agent by type.
        
        Args:
            agent_type (str): Agent type
            
        Returns:
            EnhancedAgent: First agent of the specified type or None if not found
        """
        for agent in self.agents.values():
            if agent.type == agent_type:
                return agent
        return None
    
    def start_all_agents(self):
        """Start all registered agents."""
        for agent in self.agents.values():
            agent.start()
        logger.info(f"Started {len(self.agents)} agents")
    
    def stop_all_agents(self):
        """Stop all registered agents."""
        for agent in self.agents.values():
            agent.stop()
        logger.info(f"Stopped {len(self.agents)} agents")
    
    def get_system_status(self):
        """
        Get the status of the multi-agent system.
        
        Returns:
            dict: System status information
        """
        agent_statuses = [agent.get_status() for agent in self.agents.values()]
        
        return {
            'agent_count': len(self.agents),
            'agents': agent_statuses,
            'active_tasks': len(self.task_assignments)
        }
    
    def assign_task(self, task, agent_type=None, agent_id=None):
        """
        Assign a task to an agent.
        
        Args:
            task (dict): Task definition
            agent_type (str, optional): Type of agent to assign the task to
            agent_id (str, optional): Specific agent ID to assign the task to
            
        Returns:
            str: Task ID or None if assignment failed
        """
        # Generate task ID if not provided
        if 'id' not in task:
            task['id'] = str(uuid.uuid4())
        
        # Find the appropriate agent
        agent = None
        
        if agent_id and agent_id in self.agents:
            agent = self.agents[agent_id]
        elif agent_type:
            agent = self.get_agent_by_type(agent_type)
        else:
            # Determine agent type based on task
            task_type = task.get('task_type', '')
            
            if 'financial' in task_type or task.get('symbol'):
                agent = self.get_agent_by_type('financial')
            elif 'code' in task_type or 'programming' in task_type:
                agent = self.get_agent_by_type('coding')
            elif 'research' in task_type or 'information' in task_type:
                agent = self.get_agent_by_type('research')
            
            # If still no agent found, try to find a more specialized one
            if not agent:
                if 'technical' in task_type:
                    agent = self.get_agent_by_type('technical_analysis')
                elif 'fundamental' in task_type:
                    agent = self.get_agent_by_type('fundamental_analysis')
                elif 'screen' in task_type:
                    agent = self.get_agent_by_type('stock_screener')
        
        # If still no agent found, use the first available agent
        if not agent and self.agents:
            agent = next(iter(self.agents.values()))
        
        if not agent:
            logger.error("No agents available to assign task")
            return None
        
        # Assign the task
        task_id = agent.assign_task(task)
        
        # Record the assignment
        self.task_assignments[task_id] = agent.id
        
        logger.info(f"Task {task_id} assigned to agent '{agent.name}'")
        return task_id
    
    def get_task_result(self, task_id):
        """
        Get the result of a task.
        
        Args:
            task_id (str): Task ID
            
        Returns:
            dict: Task result or status
        """
        if task_id not in self.task_assignments:
            return {'status': 'unknown', 'error': 'Task ID not found'}
        
        agent_id = self.task_assignments[task_id]
        agent = self.agents.get(agent_id)
        
        if not agent:
            return {'status': 'error', 'error': 'Agent not found'}
        
        return agent.get_result(task_id)
    
    def create_default_agents(self):
        """Create and register default agents."""
        # Create research agent
        if self.ai_engine:
            research_agent = EnhancedResearchAgent(self.ai_engine)
            self.register_agent(research_agent)
        
        # Create coding agent
        if self.ai_engine:
            coding_agent = EnhancedCodingAgent(self.ai_engine)
            self.register_agent(coding_agent)
        
        # Create financial agent
        if self.ai_engine:
            financial_agent = EnhancedFinancialAgent(self.ai_engine, self.financial_analysis_module)
            self.register_agent(financial_agent)
        
        # Create specialized financial agents
        if self.ai_engine and self.financial_analysis_module:
            # Technical analysis agent
            technical_agent = TechnicalAnalysisAgent(self.ai_engine, self.financial_analysis_module)
            self.register_agent(technical_agent)
            
            # Fundamental analysis agent
            fundamental_agent = FundamentalAnalysisAgent(self.ai_engine, self.financial_analysis_module)
            self.register_agent(fundamental_agent)
            
            # Stock screener agent
            screener_agent = StockScreenerAgent(self.ai_engine, self.financial_analysis_module)
            self.register_agent(screener_agent)
        
        logger.info(f"Created {len(self.agents)} default agents")
        
        # Start all agents
        self.start_all_agents()
        
        return len(self.agents)
