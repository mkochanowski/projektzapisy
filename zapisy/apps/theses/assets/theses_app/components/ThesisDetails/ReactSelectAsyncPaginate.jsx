/*
MIT License

Copyright (c) 2018 vtaits

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
*/

// Taken from https://github.com/vtaits/react-select-async-paginate
// FIXME maybe make a PR?

import React, { Component } from 'react';
import PropTypes from 'prop-types';

import Select from 'react-select';

const initialCache = {
  options: [],
  hasMore: true,
  isLoading: false,
  page: 0,
};

class AsyncPaginate extends Component {
  static propTypes = {
    loadOptions: PropTypes.func.isRequired,
    // eslint-disable-next-line react/forbid-prop-types
    cacheUniq: PropTypes.any,
    selectRef: PropTypes.func,
  };

  static defaultProps = {
    cacheUniq: null,
    selectRef: () => {},
  };

  state = {
    search: '',
    optionsCache: {},
  }

  componentDidUpdate({ cacheUniq }) {
    if (cacheUniq !== this.props.cacheUniq) {
      this.setState({
        optionsCache: {},
      });
    }
  }

  onClose = () => {
    this.setState({
      search: '',
    });
  }

  onOpen = async () => {
    if (!this.state.optionsCache['']) {
      await this.loadOptions();
    }
  }

  onInputChange = async (search) => {
    await this.setState({
      search,
    });

    if (!this.state.optionsCache[search]) {
      await this.loadOptions();
    }
  }

  onMenuScrollToBottom = async () => {
    const {
      search,
      optionsCache,
    } = this.state;

    const currentOptions = optionsCache[search];

    if (currentOptions) {
      await this.loadOptions();
    }
  }

  async loadOptions() {
    const {
      search,
      optionsCache,
    } = this.state;

    const currentOptions = optionsCache[search] || initialCache;

    if (currentOptions.isLoading || !currentOptions.hasMore) {
      return;
    }

    await this.setState({
      search,
      optionsCache: {
        ...this.state.optionsCache,
        [search]: {
          ...currentOptions,
          isLoading: true,
        },
      },
    });

    try {
      const {
        options,
        hasMore,
        page,
      } = await this.props.loadOptions(search, currentOptions.options, currentOptions.page);

      await this.setState({
        optionsCache: {
          ...this.state.optionsCache,
          [search]: {
            ...currentOptions,
            options: currentOptions.options.concat(options),
            hasMore: !!hasMore,
            isLoading: false,
            page,
          },
        },
      });
    } catch (e) {
      await this.setState({
        optionsCache: {
          ...this.state.optionsCache,
          [search]: {
            ...currentOptions,
            isLoading: false,
            page,
          },
        },
      });
    }
  }

  render() {
    const {
	  selectRef,
	  baseOptions,
    } = this.props;

    const {
      search,
      optionsCache,
    } = this.state;

    const currentOptions = optionsCache[search] || initialCache;
    console.warn("Rendering for", search, "with", currentOptions, "with value", this.props.value);
    let optionsToUse = currentOptions.options;

	  if (!search && !optionsToUse.length && baseOptions) {
	  	optionsToUse = baseOptions;
	  }

    return (
      <Select
        {...this.props}
        onClose={this.onClose}
        onOpen={this.onOpen}
        onInputChange={this.onInputChange}
        onMenuScrollToBottom={this.onMenuScrollToBottom}
        isLoading={currentOptions.isLoading}
        options={optionsToUse}
        ref={selectRef}
      />
    );
  }
}

export default AsyncPaginate;
