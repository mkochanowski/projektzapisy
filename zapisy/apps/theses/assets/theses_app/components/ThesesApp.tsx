import * as React from "react";
import ReactTable from "react-table";
import "react-table/react-table.css";

export function ThesesApp(props : any) {
	const data = [
		{
			name: 'Tanner Linsley',
			age: 26,
			friend: {
				name: 'Jason Maurer',
				age: 23,
			}
		},
		{
			name: 'John Doe',
			age: 49,
			friend: {
				name: 'Hank Williams',
				age: 90,
			}
		}
	];
	
	  const columns = [{
		Header: 'Name',
		accessor: 'name' // String-based value accessors!
	  }, {
		Header: 'Age',
		accessor: 'age',
		Cell: (props : any) => <span className='number'>{props.value}</span> // Custom cell components!
	  }, {
		id: 'friendName', // Required because our accessor is not a string
		Header: 'Friend Name',
		accessor: (d : any) => d.friend.name // Custom value accessors!
	  }, {
		Header: (props : any) => <span>Friend Age</span>, // Custom header components!
		accessor: 'friend.age'
	  }];
	
	return <ReactTable
		data={data}
		columns={columns}
	/>
}
